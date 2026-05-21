const doctors = [
  {
    name: "Dr. Rohit Sharma",
    specialty: "Cardiology",
    rating: "4.9",
    slot: "Today, 4:30 PM",
    location: "City Heart Hospital",
    initials: "RS",
  },
  {
    name: "Dr. Bhavya Rao",
    specialty: "Dermatology",
    rating: "4.8",
    slot: "Tomorrow, 10:00 AM",
    location: "Skin & Care Clinic",
    initials: "BR",
  },
  {
    name: "Dr. Swarna Iyer",
    specialty: "Pediatrics",
    rating: "4.9",
    slot: "Today, 6:15 PM",
    location: "Rainbow Child Care",
    initials: "SI",
  },
  {
    name: "Dr. Shashank Sen",
    specialty: "Orthopedics",
    rating: "4.7",
    slot: "Friday, 12:30 PM",
    location: "Metro Ortho Center",
    initials: "SS",
  },
];

const records = [
  { title: "Cardiology prescription", type: "Prescription", date: "21 May 2026" },
  { title: "Thyroid panel", type: "Lab report", date: "18 May 2026" },
  { title: "Chest X-ray", type: "Imaging", date: "04 May 2026" },
  { title: "Insurance approval", type: "Policy", date: "28 Apr 2026" },
];

const donors = [
  { name: "Rahul Verma", group: "O+", distance: "1.8 km", status: "Available now" },
  { name: "Priya Nair", group: "B+", distance: "2.4 km", status: "Can reach in 25 min" },
  { name: "Imran Khan", group: "AB-", distance: "4.1 km", status: "On call" },
  { name: "Leena Das", group: "A+", distance: "5.0 km", status: "Available tonight" },
];

const doctorList = document.querySelector("#doctorList");
const recordList = document.querySelector("#recordList");
const donorList = document.querySelector("#donorList");
const toast = document.querySelector("#toast");
const bookingDialog = document.querySelector("#bookingDialog");
const mainNav = document.querySelector("#mainNav");
const menuButton = document.querySelector("#menuButton");

function createIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("show"), 3000);
}

function renderDoctors(filter = "All") {
  const filtered = filter === "All" ? doctors : doctors.filter((doctor) => doctor.specialty === filter);

  doctorList.innerHTML = filtered
    .map(
      (doctor) => `
        <article class="doctor-card">
          <div class="avatar-box">${doctor.initials}</div>
          <div>
            <strong>${doctor.name}</strong>
            <p>${doctor.specialty} | ${doctor.location}</p>
            <p><i data-lucide="star"></i> ${doctor.rating} | ${doctor.slot}</p>
          </div>
          <div class="card-actions">
            <button class="secondary-button" data-doctor="${doctor.name}">
              <i data-lucide="message-circle"></i>
              Chat
            </button>
            <button class="primary-button" data-book-doctor="${doctor.name}">
              <i data-lucide="calendar-plus"></i>
              Book
            </button>
          </div>
        </article>
      `,
    )
    .join("");

  createIcons();
}

function renderRecords() {
  recordList.innerHTML = records
    .map(
      (record) => `
        <article class="record-card">
          <div class="record-icon"><i data-lucide="file-heart"></i></div>
          <div>
            <strong>${record.title}</strong>
            <p>${record.type} | ${record.date}</p>
          </div>
          <button class="icon-button" aria-label="View ${record.title}">
            <i data-lucide="eye"></i>
          </button>
        </article>
      `,
    )
    .join("");

  createIcons();
}

function renderDonors() {
  donorList.innerHTML = donors
    .map(
      (donor) => `
        <article class="donor-card">
          <div class="donor-avatar">${donor.group}</div>
          <div>
            <strong>${donor.name}</strong>
            <p>${donor.distance} | ${donor.status}</p>
          </div>
          <button class="secondary-button" data-toast="Contact request sent to ${donor.name}.">
            <i data-lucide="phone"></i>
            Contact
          </button>
        </article>
      `,
    )
    .join("");

  createIcons();
}

function closeMenu() {
  mainNav.classList.remove("open");
  menuButton.setAttribute("aria-expanded", "false");
  document.body.classList.remove("menu-open");
}

menuButton.addEventListener("click", () => {
  const isOpen = mainNav.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
  document.body.classList.toggle("menu-open", isOpen);
});

document.querySelectorAll(".main-nav a").forEach((link) => {
  link.addEventListener("click", closeMenu);
});

document.addEventListener("click", (event) => {
  const bookingTrigger = event.target.closest("[data-open-booking]");
  const bookDoctor = event.target.closest("[data-book-doctor]");
  const doctorMessage = event.target.closest("[data-doctor]");
  const toastButton = event.target.closest("[data-toast]");

  if (bookingTrigger) {
    bookingDialog.showModal();
  }

  if (bookDoctor) {
    bookingDialog.showModal();
    showToast(`Booking started with ${bookDoctor.dataset.bookDoctor}.`);
  }

  if (doctorMessage) {
    showToast(`Secure chat opened with ${doctorMessage.dataset.doctor}.`);
  }

  if (toastButton) {
    showToast(toastButton.dataset.toast);
  }
});

document.querySelectorAll("[data-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderDoctors(button.dataset.filter);
  });
});

document.querySelector("#confirmBooking").addEventListener("click", (event) => {
  event.preventDefault();
  bookingDialog.close();
  showToast("Appointment request confirmed. The care desk will send the final slot details.");
});

document.querySelector("#uploadRecordButton").addEventListener("click", () => {
  records.unshift({
    title: "New uploaded record",
    type: "Document",
    date: "Just now",
  });
  renderRecords();
  showToast("Record added to the health vault.");
});

document.querySelector("#donorForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);

  donors.unshift({
    name: `${formData.get("group")} urgent request`,
    group: formData.get("group"),
    distance: formData.get("hospital"),
    status: `For ${formData.get("patient")}`,
  });

  renderDonors();
  showToast("Blood donor request sent to nearby verified donors.");
  event.currentTarget.reset();
});

function init() {
  renderDoctors();
  renderRecords();
  renderDonors();
  createIcons();
}

init();
