import { Component, inject, OnInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { RecordService } from '../../core/services/record.service';
import { AuthService } from '../../core/services/auth.service';
import { MedicalRecord } from '../../core/models/record.model';

@Component({
  selector: 'app-records',
  standalone: true,
  imports: [CommonModule, NavbarComponent, RouterLink, FormsModule],
  templateUrl: './records.component.html',
  styleUrl: './records.component.css'
})
export class RecordsComponent implements OnInit {
  recordService = inject(RecordService);
  auth = inject(AuthService);
  sanitizer = inject(DomSanitizer);
  route = inject(ActivatedRoute);

  @ViewChild('fileInput') fileInput!: ElementRef;

  patientId: string | null = null;
  records: MedicalRecord[] = [];
  categories: string[] = [];
  loading = true;
  selectedCategory = '';
  successMsg = '';
  errorMsg = '';

  // Upload modal state
  showUpload = false;
  uploadLoading = false;
  uploadError = '';
  selectedFile: File | null = null;
  uploadForm = {
    title: '',
    category: 'Other',
    description: '',
    doctor_name: '',
    record_date: ''
  };

  // Preview modal state
  previewRecord: MedicalRecord | null = null;
  previewUrl: string | null = null;
  safePreviewUrl: SafeResourceUrl | null = null;
  deletingId: string | null = null;

  get user() { return this.auth.currentUser(); }
  get isDoctor() { return this.user?.role === 'DOCTOR'; }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.patientId = params['patientId'] || null;
      this.loadCategories();
      this.loadRecords();
    });
  }

  loadCategories() {
    this.recordService.getCategories().subscribe({
      next: (res) => { if (res.success && res.data) this.categories = res.data; }
    });
  }

  loadRecords() {
    this.loading = true;
    this.recordService.getRecords(this.selectedCategory || undefined, this.patientId || undefined).subscribe({
      next: (res) => {
        if (res.success && res.data) this.records = res.data;
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  onCategoryFilter() { this.loadRecords(); }

  // ── Upload ──────────────────────────────────────────────────────
  openUpload() {
    this.showUpload = true;
    this.uploadError = '';
    this.selectedFile = null;
    this.uploadForm = { title: '', category: 'Other', description: '', doctor_name: '', record_date: '' };
  }

  closeUpload() { this.showUpload = false; }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      const allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
      if (!allowed.includes(file.type)) {
        this.uploadError = 'Only PDF and image files are allowed.';
        this.selectedFile = null;
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        this.uploadError = 'File must be under 10 MB.';
        this.selectedFile = null;
        return;
      }
      this.selectedFile = file;
      this.uploadError = '';
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const files = event.dataTransfer?.files;
    if (files && files[0]) {
      const fakeEvent = { target: { files } } as unknown as Event;
      this.onFileSelect(fakeEvent);
    }
  }

  onDragOver(event: DragEvent) { event.preventDefault(); }

  submitUpload() {
    if (!this.uploadForm.title.trim()) { this.uploadError = 'Title is required.'; return; }
    if (!this.selectedFile) { this.uploadError = 'Please select a file.'; return; }

    this.uploadLoading = true;
    this.uploadError = '';

    const fd = new FormData();
    fd.append('file', this.selectedFile);
    fd.append('title', this.uploadForm.title);
    fd.append('category', this.uploadForm.category);
    fd.append('description', this.uploadForm.description);
    fd.append('doctor_name', this.uploadForm.doctor_name);
    fd.append('record_date', this.uploadForm.record_date);

    this.recordService.uploadRecord(fd).subscribe({
      next: (res) => {
        if (res.success) {
          this.successMsg = 'Record uploaded successfully!';
          this.showUpload = false;
          this.loadRecords();
          setTimeout(() => this.successMsg = '', 4000);
        } else {
          this.uploadError = res.message || 'Upload failed.';
        }
        this.uploadLoading = false;
      },
      error: (err: { error?: { message?: string } }) => {
        this.uploadError = err.error?.message || 'Upload failed.';
        this.uploadLoading = false;
      }
    });
  }

  // ── Preview ──────────────────────────────────────────────────────
  openPreview(record: MedicalRecord) {
    this.previewRecord = record;
    this.previewUrl = null;
    this.safePreviewUrl = null;
    this.recordService.downloadRecord(record.id).subscribe({
      next: (blob) => {
        const rawUrl = URL.createObjectURL(blob);
        this.previewUrl = rawUrl;
        this.safePreviewUrl = this.sanitizer.bypassSecurityTrustResourceUrl(rawUrl);
      },
      error: () => {
        this.previewUrl = '';
        this.safePreviewUrl = null;
      }
    });
  }

  closePreview() {
    this.previewRecord = null;
    this.safePreviewUrl = null;
    if (this.previewUrl) {
      URL.revokeObjectURL(this.previewUrl);
      this.previewUrl = null;
    }
  }

  isImage(record: MedicalRecord): boolean {
    return record.file_type?.startsWith('image/') ?? false;
  }

  isPdf(record: MedicalRecord): boolean {
    return record.file_type === 'application/pdf';
  }

  // ── Download ──────────────────────────────────────────────────────
  downloadRecord(record: MedicalRecord) {
    this.recordService.downloadRecord(record.id).subscribe({
      next: (blob) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = record.file_name;
        a.click();
        URL.revokeObjectURL(a.href);
      }
    });
  }

  // ── Delete ──────────────────────────────────────────────────────
  deleteRecord(id: string) {
    if (!confirm('Are you sure you want to permanently delete this record?')) return;
    this.deletingId = id;
    this.recordService.deleteRecord(id).subscribe({
      next: (res) => {
        if (res.success) {
          this.successMsg = 'Record deleted.';
          this.loadRecords();
          if (this.previewRecord?.id === id) this.closePreview();
          setTimeout(() => this.successMsg = '', 3000);
        }
        this.deletingId = null;
      },
      error: () => { this.deletingId = null; }
    });
  }

  // ── Helpers ──────────────────────────────────────────────────────
  formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  categoryColor(cat: string): string {
    const map: Record<string, string> = {
      'Prescription':       'cat-prescription',
      'Blood Test':         'cat-blood',
      'Scan / X-Ray':       'cat-scan',
      'MRI':                'cat-mri',
      'Vaccination':        'cat-vaccine',
      'Lab Report':         'cat-lab',
      'Discharge Summary':  'cat-discharge',
      'Other':              'cat-other',
    };
    return map[cat] || 'cat-other';
  }

  categoryIcon(cat: string): string {
    const map: Record<string, string> = {
      'Prescription':       'Rx',
      'Blood Test':         'BT',
      'Scan / X-Ray':       'XR',
      'MRI':                'MR',
      'Vaccination':        'VC',
      'Lab Report':         'LR',
      'Discharge Summary':  'DS',
      'Other':              'OT',
    };
    return map[cat] || '?';
  }
}
