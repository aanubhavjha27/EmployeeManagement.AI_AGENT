package com.employee.employemgmt.service;

import com.employee.employemgmt.entity.employee;
import com.employee.employemgmt.repository.employeerepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class employeeservice {

    @Autowired
    private employeerepository repo;

    public List<employee> getallemployees() {
        return repo.findAll();
    }

    public employee addemployee(employee employee) {
        if (repo.existsByEmail(employee.getEmail())) {
            throw new RuntimeException("employee with this email already exists");
        }
        return repo.save(employee);
    }

    public void deleteemployee(Long id) {
        repo.deleteById(id);
    }

    public Optional<employee> getemployeebyid(Long id) {
        return repo.findById(id);
    }

    // ✅ PARTIAL UPDATE (agent-friendly): only overwrite fields that are NOT null
    public ResponseEntity<?> updateemployeebyid(Long id, employee incoming) {

        Optional<employee> optionalEmployee = repo.findById(id);
        if (optionalEmployee.isEmpty()) {
            return new ResponseEntity<>("Employee not found with id: " + id, HttpStatus.NOT_FOUND);
        }

        employee old = optionalEmployee.get();

        if (incoming.getFirstname() != null) old.setFirstname(incoming.getFirstname());
        if (incoming.getLastname() != null) old.setLastname(incoming.getLastname());
        if (incoming.getEmail() != null) old.setEmail(incoming.getEmail());
        if (incoming.getGender() != null) old.setGender(incoming.getGender());
        if (incoming.getAge() != null) old.setAge(incoming.getAge());
        if (incoming.getJoiningDate() != null) old.setJoiningDate(incoming.getJoiningDate());
        if (incoming.getReferredBy() != null) old.setReferredBy(incoming.getReferredBy());
        if (incoming.getPhoneNumber() != null) old.setPhoneNumber(incoming.getPhoneNumber());
        if (incoming.getDepartment() != null) old.setDepartment(incoming.getDepartment());
        if (incoming.getPosition() != null) old.setPosition(incoming.getPosition());
        if (incoming.getSalary() != null) old.setSalary(incoming.getSalary());
        if (incoming.getAddress() != null) old.setAddress(incoming.getAddress());
        if (incoming.getCity() != null) old.setCity(incoming.getCity());
        if (incoming.getState() != null) old.setState(incoming.getState());
        if (incoming.getCountry() != null) old.setCountry(incoming.getCountry());
        if (incoming.getStatus() != null) old.setStatus(incoming.getStatus());

        employee saved = repo.save(old);
        return new ResponseEntity<>(saved, HttpStatus.OK);
    }

    public List<employee> searchEmployees(String name, String email, String phoneNumber) {

        // Priority: email > phone > name

        if (email != null && !email.isEmpty()) {
            return repo.findByEmail(email)
                    .map(List::of)
                    .orElse(List.of());
        }

        if (phoneNumber != null && !phoneNumber.isEmpty()) {
            return repo.findByPhoneNumber(phoneNumber);
        }

        if (name != null && !name.isEmpty()) {
            return repo.searchByName(name);
        }

        return List.of();
    }

    public List<employee> filterbygender(String gender) {
        return repo.findByGenderIgnoreCase(gender);
    }
}