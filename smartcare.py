# LIFECARE+ SMART HEALTH SYSTEM

import json
import os
from datetime import datetime

# ANSI Escape codes for colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ------------------ Data Models ------------------

class Doctor:
    def __init__(self, doc_id, name, specialization, fee, slot1, slot2, accepts_insurance=True, schedule=None):
        self.doc_id = doc_id
        self.name = name
        self.specialization = specialization
        self.fee = fee
        self.slot1 = slot1
        self.slot2 = slot2
        self.accepts_insurance = accepts_insurance
        self.schedule = schedule if schedule else {}

    def is_slot_available(self, date_str, slot):
        day = self.schedule.get(date_str, {'slot1': [], 'slot2': []})
        return len(day.get(slot, [])) == 0

    def book_slot(self, date_str, slot, patient_id):
        if date_str not in self.schedule:
            self.schedule[date_str] = {'slot1': [], 'slot2': []}
        if patient_id not in self.schedule[date_str][slot]:
            self.schedule[date_str][slot].append(patient_id)

    def cancel_slot(self, date_str, slot, patient_id):
        if date_str in self.schedule and patient_id in self.schedule[date_str].get(slot, []):
            self.schedule[date_str][slot].remove(patient_id)

    def __str__(self):
        ins = f"{Colors.OKGREEN}Yes{Colors.ENDC}" if self.accepts_insurance else f"{Colors.FAIL}No{Colors.ENDC}"
        return f"{Colors.OKCYAN}ID:{self.doc_id}{Colors.ENDC} | {Colors.BOLD}{self.name}{Colors.ENDC} ({self.specialization}) | Fee: ₹{self.fee} | Insurance: {ins}\n  Slots: 1) {self.slot1}  2) {self.slot2}"

    def to_dict(self):
        return {
            'doc_id': self.doc_id,
            'name': self.name,
            'specialization': self.specialization,
            'fee': self.fee,
            'slot1': self.slot1,
            'slot2': self.slot2,
            'accepts_insurance': self.accepts_insurance,
            'schedule': self.schedule
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Patient:
    def __init__(self, patient_id, name, phone, is_member=False,
                 membership_type=None, family_members=None,
                 has_insurance=False, insurance_provider=None, health_score=70):
        self.patient_id = patient_id
        self.name = name
        self.phone = phone
        self.is_member = is_member
        self.membership_type = membership_type
        self.family_members = family_members or []
        self.has_insurance = has_insurance
        self.insurance_provider = insurance_provider
        self.health_score = health_score

    def __str__(self):
        mem = f"{Colors.OKGREEN}Member ({self.membership_type}){Colors.ENDC}" if self.is_member else "No"
        ins = f"{Colors.OKGREEN}Yes ({self.insurance_provider}){Colors.ENDC}" if self.has_insurance else "No"
        score_color = Colors.OKGREEN if self.health_score >= 70 else Colors.WARNING
        return f"{Colors.OKCYAN}ID:{self.patient_id}{Colors.ENDC} | {Colors.BOLD}{self.name}{Colors.ENDC} | Phone:{self.phone} | Member:{mem} | Insurance:{ins} | {score_color}Health Score:{self.health_score}/100{Colors.ENDC}"

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'phone': self.phone,
            'is_member': self.is_member,
            'membership_type': self.membership_type,
            'family_members': self.family_members,
            'has_insurance': self.has_insurance,
            'insurance_provider': self.insurance_provider,
            'health_score': self.health_score
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


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
        ins_str = f"{Colors.OKGREEN}Yes{Colors.ENDC}" if self.via_insurance else "No"
        return f"{Colors.WARNING}ApptID:{self.appt_id}{Colors.ENDC} | PatID:{self.patient_id} | DocID:{self.doctor_id} | Date:{self.date_str} | Slot:{self.slot} | Amount: ₹{self.amount} | Insurance: {ins_str}"

    def to_dict(self):
        return {
            'appt_id': self.appt_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date_str': self.date_str,
            'slot': self.slot,
            'paid': self.paid,
            'payment_method': self.payment_method,
            'amount': self.amount,
            'via_insurance': self.via_insurance
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ------------------ Hospital System ------------------

class HospitalSystem:
    APP_PAYMENT_DISCOUNT = 0.10
    MEMBER_FEE_DISCOUNT = 0.15
    DATA_FILE = "hospital_data.json"

    def __init__(self):
        self.doctors = {}
        self.patients = {}
        self.appointments = {}
        self.next_doc_id = 1
        self.next_patient_id = 1
        self.next_appt_id = 1
        self.load_data()

    def save_data(self):
        data = {
            'doctors': {doc_id: doc.to_dict() for doc_id, doc in self.doctors.items()},
            'patients': {pat_id: pat.to_dict() for pat_id, pat in self.patients.items()},
            'appointments': {appt_id: appt.to_dict() for appt_id, appt in self.appointments.items()},
            'counters': {
                'next_doc_id': self.next_doc_id,
                'next_patient_id': self.next_patient_id,
                'next_appt_id': self.next_appt_id
            }
        }
        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"{Colors.FAIL}Error saving data: {e}{Colors.ENDC}")

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)
                    
                self.doctors = {int(k): Doctor.from_dict(v) for k, v in data.get('doctors', {}).items()}
                self.patients = {int(k): Patient.from_dict(v) for k, v in data.get('patients', {}).items()}
                self.appointments = {int(k): Appointment.from_dict(v) for k, v in data.get('appointments', {}).items()}
                
                counters = data.get('counters', {})
                self.next_doc_id = counters.get('next_doc_id', 1)
                self.next_patient_id = counters.get('next_patient_id', 1)
                self.next_appt_id = counters.get('next_appt_id', 1)
            except Exception as e:
                print(f"{Colors.FAIL}Error loading data: {e}. Starting fresh.{Colors.ENDC}")
                self.seed_sample_data()
        else:
            self.seed_sample_data()

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
                print(f"{Colors.OKGREEN}► Suggested Specialization: {spec}{Colors.ENDC}")
                return
        print(f"{Colors.WARNING}► No specific suggestion found for '{symptom}'. Try searching by specialization.{Colors.ENDC}")

    def seed_sample_data(self):
        self.add_doctor("Dr. Aakash Sharma", "General Physician",
                        500, "09:00-11:00", "16:00-18:00", True)
        self.add_doctor("Dr. Neha Kulkarni", "Pediatrics", 700,
                        "10:00-12:00", "15:00-17:00", True)
        self.add_doctor("Dr. Rahul Mehta", "Orthopedics", 1200,
                        "11:00-13:00", "17:00-19:00", False)
        self.save_data()

    def add_doctor(self, name, specialization, fee, slot1, slot2, accepts_insurance=True):
        doc = Doctor(self.next_doc_id, name, specialization,
                     fee, slot1, slot2, accepts_insurance)
        self.doctors[self.next_doc_id] = doc
        self.next_doc_id += 1
        self.save_data()
        print(f"{Colors.OKGREEN}Doctor added successfully!{Colors.ENDC}")

    def list_doctors(self):
        if not self.doctors:
            print(f"{Colors.WARNING}No doctors found.{Colors.ENDC}")
            return
        for d in self.doctors.values():
            print(d)

    def add_patient(self, name, phone, is_member=False, membership_type=None,
                    family_members=None, has_insurance=False, insurance_provider=None):
        pat = Patient(self.next_patient_id, name, phone, is_member,
                      membership_type, family_members, has_insurance, insurance_provider)
        self.patients[self.next_patient_id] = pat
        print(f"{Colors.OKGREEN}Patient registered with ID {self.next_patient_id}{Colors.ENDC}")
        self.next_patient_id += 1
        self.save_data()

    def list_patients(self):
        if not self.patients:
            print(f"{Colors.WARNING}No patients found.{Colors.ENDC}")
            return
        for p in self.patients.values():
            print(p)

    def book_appointment(self, patient_id, doctor_id, date_str, slot, pay_with_app=False, use_insurance=False):
        pat = self.patients.get(patient_id)
        doc = self.doctors.get(doctor_id)

        if not pat or not doc:
            print(f"{Colors.FAIL}Invalid Patient ID or Doctor ID.{Colors.ENDC}")
            return

        if not doc.is_slot_available(date_str, slot):
            print(f"{Colors.FAIL}Slot already booked. Please choose another slot or date.{Colors.ENDC}")
            return

        amount = doc.fee
        via_insurance = False

        if use_insurance:
            if not pat.has_insurance or not doc.accepts_insurance:
                print(f"{Colors.FAIL}Insurance not applicable. Either patient has no insurance or doctor doesn't accept it.{Colors.ENDC}")
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

        pat.health_score = min(100, pat.health_score + 5)
        
        self.save_data()
        print(f"{Colors.OKGREEN}Appointment booked successfully!{Colors.ENDC}")
        print(appt)

    def cancel_appointment(self, appt_id):
        appt = self.appointments.get(appt_id)
        if not appt:
            print(f"{Colors.FAIL}Invalid appointment ID.{Colors.ENDC}")
            return

        doc = self.doctors.get(appt.doctor_id)
        pat = self.patients.get(appt.patient_id)

        if doc:
            doc.cancel_slot(appt.date_str, appt.slot, appt.patient_id)

        if pat:
            pat.health_score = max(0, pat.health_score - 10)

        del self.appointments[appt_id]
        self.save_data()
        print(f"{Colors.OKGREEN}Appointment cancelled successfully. Health score updated.{Colors.ENDC}")

    def list_appointments(self):
        if not self.appointments:
            print(f"{Colors.WARNING}No appointments found.{Colors.ENDC}")
            return
        for a in self.appointments.values():
            print(a)

    def buy_membership(self, patient_id, membership_type, family_members=None):
        pat = self.patients.get(patient_id)
        if not pat:
            print(f"{Colors.FAIL}Invalid patient ID.{Colors.ENDC}")
            return
        pat.is_member = True
        pat.membership_type = membership_type
        if membership_type == "family":
            pat.family_members = family_members or []
        self.save_data()
        print(f"{Colors.OKGREEN}Membership activated successfully!{Colors.ENDC}")


# ------------------ Console Menu ------------------

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    hs = HospitalSystem()

    while True:
        print(f"\n{Colors.HEADER}{Colors.BOLD}=== LifeCare+ Smart Health System ==={Colors.ENDC}")
        print("1. List Doctors")
        print("2. Add Doctor")
        print("3. List Patients")
        print("4. Register Patient")
        print("5. Book Appointment")
        print("6. Cancel Appointment")
        print("7. List Appointments")
        print("8. Buy Membership")
        print(f"{Colors.FAIL}9. Exit{Colors.ENDC}")

        choice = input(f"{Colors.OKBLUE}Choose option (1-9): {Colors.ENDC}")

        if choice == '1':
            print(f"\n{Colors.HEADER}--- Doctors List ---{Colors.ENDC}")
            hs.list_doctors()

        elif choice == '2':
            print(f"\n{Colors.HEADER}--- Add Doctor ---{Colors.ENDC}")
            try:
                name = input("Name: ")
                specialization = input("Specialization: ")
                fee = float(input("Fee (e.g. 500): "))
                slot1 = input("Slot 1 (e.g. 09:00-11:00): ")
                slot2 = input("Slot 2 (e.g. 16:00-18:00): ")
                ins = input("Accept insurance? (y/n): ").lower() == 'y'
                hs.add_doctor(name, specialization, fee, slot1, slot2, ins)
            except ValueError:
                print(f"{Colors.FAIL}Invalid input. Fee must be a number.{Colors.ENDC}")

        elif choice == '3':
            print(f"\n{Colors.HEADER}--- Patients List ---{Colors.ENDC}")
            hs.list_patients()

        elif choice == '4':
            print(f"\n{Colors.HEADER}--- Register Patient ---{Colors.ENDC}")
            name = input("Patient name: ")
            phone = input("Phone: ")
            ins = input("Has insurance? (y/n): ").lower() == 'y'
            provider = input("Insurance provider (press enter if none): ") if ins else None
            hs.add_patient(name, phone, has_insurance=ins, insurance_provider=provider)

        elif choice == '5':
            print(f"\n{Colors.HEADER}--- Book Appointment ---{Colors.ENDC}")
            symptom = input("Enter symptom to get doctor suggestion (or press enter to skip): ")
            if symptom.strip():
                hs.suggest_doctor_by_symptom(symptom)

            try:
                pid = int(input("Patient ID: "))
                did = int(input("Doctor ID: "))
                date = input("Date (YYYY-MM-DD): ")
                slot_choice = input("Slot (1/2): ")
                slot = 'slot1' if slot_choice == '1' else 'slot2'
                pay = input("Payment online? (y/n): ").lower() == 'y'
                use_ins = input("Use insurance? (y/n): ").lower() == 'y'
                hs.book_appointment(pid, did, date, slot, pay, use_ins)
            except ValueError:
                print(f"{Colors.FAIL}Invalid input. ID fields must be numbers.{Colors.ENDC}")

        elif choice == '6':
            print(f"\n{Colors.HEADER}--- Cancel Appointment ---{Colors.ENDC}")
            try:
                appt_id = int(input("Appointment ID to cancel: "))
                hs.cancel_appointment(appt_id)
            except ValueError:
                print(f"{Colors.FAIL}Invalid input. Appointment ID must be a number.{Colors.ENDC}")

        elif choice == '7':
            print(f"\n{Colors.HEADER}--- Appointments List ---{Colors.ENDC}")
            hs.list_appointments()

        elif choice == '8':
            print(f"\n{Colors.HEADER}--- Buy Membership ---{Colors.ENDC}")
            try:
                pid = int(input("Patient ID: "))
                mtype = input("Membership (individual/family): ").lower()
                family = None
                if mtype == "family":
                    family = input("Family members (comma separated): ").split(',')
                hs.buy_membership(pid, mtype, family)
            except ValueError:
                print(f"{Colors.FAIL}Invalid input. Patient ID must be a number.{Colors.ENDC}")

        elif choice == '9':
            print(f"{Colors.OKGREEN}Saving data... Exiting LifeCare+. Stay Healthy!{Colors.ENDC}")
            break

        else:
            print(f"{Colors.FAIL}Invalid choice. Please pick a number from 1 to 9.{Colors.ENDC}")


if __name__ == "__main__":
    # Workaround for Windows CMD to support ANSI colors
    if os.name == 'nt':
        os.system('color')
    main_menu()
