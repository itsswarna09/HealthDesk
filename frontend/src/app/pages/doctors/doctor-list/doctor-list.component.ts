import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/navbar/navbar.component';
import { DoctorService } from '../../../core/services/doctor.service';
import { Doctor } from '../../../core/models/doctor.model';

@Component({
  selector: 'app-doctor-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, NavbarComponent],
  templateUrl: './doctor-list.component.html',
  styleUrl: './doctor-list.component.css'
})
export class DoctorListComponent implements OnInit {
  doctorService = inject(DoctorService);

  doctors: Doctor[] = [];
  loading = true;
  searchTerm = '';
  selectedSpecialization = '';
  
  // Dynamic list of unique specializations derived from loaded doctors
  specializations: string[] = [];

  ngOnInit() {
    this.loadSpecializations();
    this.loadDoctors();
  }

  loadSpecializations() {
    this.doctorService.getSpecializations().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.specializations = res.data;
        }
      }
    });
  }

  errorMessage = '';

  loadDoctors() {
    this.loading = true;
    this.errorMessage = '';
    this.doctorService.getDoctors(this.selectedSpecialization).subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.doctors = res.data;
        } else {
          this.errorMessage = 'API returned success: false or empty data';
        }
        this.loading = false;
      },
      error: (err) => {
        this.errorMessage = `HTTP Error: ${err.message || JSON.stringify(err)}`;
        this.loading = false;
      }
    });
  }

  onFilterChange() {
    this.loadDoctors();
  }

  get filteredDoctors() {
    if (!this.searchTerm.trim()) {
      return this.doctors;
    }
    const term = this.searchTerm.toLowerCase();
    return this.doctors.filter(d => {
      const nameMatch = d.user?.full_name?.toLowerCase().includes(term);
      const specMatch = d.specialization?.toLowerCase().includes(term);
      return nameMatch || specMatch;
    });
  }


}
