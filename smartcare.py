# LIFECARE+ SMART HEALTH SYSTEM

from datetime import datetime

# ------------------ Data Models ------------------


class Doctor:
    def __init__(self, doc_id, name, specialization, fee, slot1, slot2, accepts_insurance=True):
        self.doc_id = doc_id
        self.name = name
        self.specialization = specialization
        self.fee = fee
        self.slot1 = slot1
        self.slot2 = slot2
        self.accepts_insurance = accepts_insurance
        self.schedule = {}

    def is_slot_available(self, date_str, slot):
        day = self.schedule.get(date_str, {'slot1': [], 'slot2': []})
        return len(day.get(slot, [])) == 0

    def book_slot(self, date_str, slot, patient_id):
        if date_str not in self.schedule:
            self.schedule[date_str] = {'slot1': [], 'slot2': []}
        self.schedule[date_str][slot].append(patient_id)

    def cancel_slot(self, date_str, slot, patient_id):
        if date_str in self.schedule and patient_id in self.schedule[date_str].get(slot, []):
            self.schedule[date_str][slot].remove(patient_id)

    def __str__(self):
        ins = "Yes" if self.accepts_insurance else "No"
        return f"ID:{self.doc_id} | {self.name} ({self.specialization}) | Fee:{self.fee} | Insurance:{ins}\n Slots: 1){self.slot1}  2){self.slot2}"


class Patient:
    def __init__(self, patient_id, name, phone, is_member=False,
                 membership_type=None, family_members=None,
                 has_insurance=False, insurance_provider=None):
        self.patient_id = patient_id
        self.name = name
        self.phone = phone
        self.is_member = is_member
        self.membership_type = membership_type
        self.family_members = family_members or []
        self.has_insurance = has_insurance
        self.insurance_provider = insurance_provider

        # ✅ Health Score Passport
        self.health_score = 70

    def __str__(self):
        mem = f"Member ({self.membership_type})" if self.is_member else "No"
        ins = f"Yes ({self.insurance_provider})" if self.has_insurance else "No"
        return f"ID:{self.patient_id} | {self.name} | Phone:{self.phone} | Member:{mem} | Insurance:{ins} | Health Score:{self.health_score}/100"


class Appointment:
    def __init__(self, appt_id, patient_id, doctor_id, date_str, slot,
                 paid=False, payment_method=None, amount=0.0, via_insurance=False):
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date_str = date_str
        self.slot = slot
        self.paid = paid
        self.payment_method = payment_method
        self.amount = amount
        self.via_insurance = via_insurance

    def __str__(self):
        return f"ApptID:{self.appt_id} | Patient:{self.patient_id} | Doctor:{self.doctor_id} | Date:{self.date_str} | Slot:{self.slot} | Amount:{self.amount} | Insurance:{'Yes' if self.via_insurance else 'No'}"


# ------------------ Hospital System ------------------


class HospitalSystem:
    APP_PAYMENT_DISCOUNT = 0.10
    MEMBER_FEE_DISCOUNT = 0.15

    def __init__(self):
        self.doctors = {}
        self.patients = {}
        self.appointments = {}
        self.next_doc_id = 1
        self.next_patient_id = 1
        self.next_appt_id = 1
        self.seed_sample_data()

    # ---------- NEW FEATURE ----------
    def suggest_doctor_by_symptom(self, symptom):
        mapping = {
            "fever": "General Physician",
            "cold": "General Physician",
            "body": "General Physician",
            "bone": "Orthopedics",
            "joint": "Orthopedics",
            "fracture": "Orthopedics",
            "child": "Pediatrics",
            "baby": "Pediatrics"
        }
        symptom = symptom.lower()
        for key, spec in mapping.items():
            if key in symptom:
                print(f"Suggested Doctor: {spec}")
                return
        print("No specific doctor suggestion.")

    def seed_sample_data(self):
        self.add_doctor("Dr. Aakash Sharma", "General Physician",
                        500, "09:00-11:00", "16:00-18:00", True)
        self.add_doctor("Dr. Neha Kulkarni", "Pediatrics", 700,
                        "10:00-12:00", "15:00-17:00", True)
        self.add_doctor("Dr. Rahul Mehta", "Orthopedics", 1200,
                        "11:00-13:00", "17:00-19:00", False)

    # ---------- Doctor Operations ----------
    def add_doctor(self, name, specialization, fee, slot1, slot2, accepts_insurance=True):
        doc = Doctor(self.next_doc_id, name, specialization,
                     fee, slot1, slot2, accepts_insurance)
        self.doctors[self.next_doc_id] = doc
        self.next_doc_id += 1

    def list_doctors(self):
        for d in self.doctors.values():
            print(d)

    # ---------- Patient Operations ----------
    def add_patient(self, name, phone, is_member=False, membership_type=None,
                    family_members=None, has_insurance=False, insurance_provider=None):
        pat = Patient(self.next_patient_id, name, phone, is_member,
                      membership_type, family_members, has_insurance, insurance_provider)
        self.patients[self.next_patient_id] = pat
        print(f"Patient registered with ID {self.next_patient_id}")
        self.next_patient_id += 1

    def list_patients(self):
        for p in self.patients.values():
            print(p)

    # ---------- Appointment Operations ----------
    def book_appointment(self, patient_id, doctor_id, date_str, slot, pay_with_app=False, use_insurance=False):
        pat = self.patients.get(patient_id)
        doc = self.doctors.get(doctor_id)

        if not pat or not doc:
            print("Invalid ID")
            return

        if not doc.is_slot_available(date_str, slot):
            print("Slot already booked")
            return

        amount = doc.fee
        via_insurance = False

        if use_insurance:
            if not pat.has_insurance or not doc.accepts_insurance:
                print("Insurance not applicable")
                return
            amount = 0
            via_insurance = True
        else:
            if pay_with_app:
                amount -= amount * self.APP_PAYMENT_DISCOUNT
            if pat.is_member:
                amount -= amount * self.MEMBER_FEE_DISCOUNT

        appt = Appointment(self.next_appt_id, patient_id, doctor_id,
                           date_str, slot, paid=(amount == 0),
                           payment_method="online" if pay_with_app else "cash",
                           amount=round(amount, 2), via_insurance=via_insurance)

        self.appointments[self.next_appt_id] = appt
        self.next_appt_id += 1
        doc.book_slot(date_str, slot, patient_id)

        # Health score reward
        pat.health_score = min(100, pat.health_score + 5)

        print("Appointment booked successfully")
        print(appt)

    def cancel_appointment(self, appt_id):
        appt = self.appointments.get(appt_id)
        if not appt:
            print("Invalid appointment ID")
            return

        doc = self.doctors.get(appt.doctor_id)
        pat = self.patients.get(appt.patient_id)

        if doc:
            doc.cancel_slot(appt.date_str, appt.slot, appt.patient_id)

        if pat:
            pat.health_score = max(0, pat.health_score - 10)

        del self.appointments[appt_id]
        print("Appointment cancelled")

    def list_appointments(self):
        for a in self.appointments.values():
            print(a)

    # ---------- Membership ----------
    def buy_membership(self, patient_id, membership_type, family_members=None):
        pat = self.patients.get(patient_id)
        if not pat:
            print("Invalid patient ID")
            return
        pat.is_member = True
        pat.membership_type = membership_type
        if membership_type == "family":
            pat.family_members = family_members or []
        print("Membership activated successfully")


# ------------------ Console Menu ------------------

def main_menu():
    hs = HospitalSystem()

    while True:
        print("\n=== LifeCare+ Smart Health System ===")
        print("1. List Doctors")
        print("2. Add Doctor")
        print("3. List Patients")
        print("4. Register Patient")
        print("5. Book Appointment")
        print("6. Cancel Appointment")
        print("7. List Appointments")
        print("8. Buy Membership")
        print("9. Exit")

        choice = input("Choose option: ")

        if choice == '1':
            hs.list_doctors()

        elif choice == '2':
            hs.add_doctor(
                input("Name: "),
                input("Specialization: "),
                float(input("Fee: ")),
                input("Slot 1: "),
                input("Slot 2: "),
                input("Accept insurance? (y/n): ").lower() == 'y'
            )

        elif choice == '3':
            hs.list_patients()

        elif choice == '4':
            name = input("Patient name: ")
            phone = input("Phone: ")
            ins = input("Has insurance? (y/n): ").lower() == 'y'
            provider = input("Insurance provider: ") if ins else None
            hs.add_patient(name, phone, has_insurance=ins,
                           insurance_provider=provider)

        elif choice == '5':
            symptom = input("Enter symptom: ")
            hs.suggest_doctor_by_symptom(symptom)

            pid = int(input("Patient ID: "))
            did = int(input("Doctor ID: "))
            date = input("Date (YYYY-MM-DD): ")
            slot = 'slot1' if input("Slot (1/2): ") == '1' else 'slot2'
            pay = input("Payment (online/cash): ") == 'online'
            use_ins = input("Use insurance? (y/n): ") == 'y'
            hs.book_appointment(pid, did, date, slot, pay, use_ins)

        elif choice == '6':
            hs.cancel_appointment(int(input("Appointment ID: ")))

        elif choice == '7':
            hs.list_appointments()

        elif choice == '8':
            pid = int(input("Patient ID: "))
            mtype = input("Membership (individual/family): ")
            family = None
            if mtype == "family":
                family = input("Family members (comma separated): ").split(',')
            hs.buy_membership(pid, mtype, family)

        elif choice == '9':
            print("Exiting LifeCare+")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main_menu()
