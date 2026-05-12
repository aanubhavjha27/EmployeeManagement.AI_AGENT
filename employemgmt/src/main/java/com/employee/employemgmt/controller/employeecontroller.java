package com.employee.employemgmt.controller;


import com.employee.employemgmt.entity.employee;
import com.employee.employemgmt.service.employeeservice;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@CrossOrigin(origins = "http://localhost:5173")
@RequestMapping("/api")
public class employeecontroller {

    @GetMapping("/")
    public String greet(){
        return "hello world";
    }

    @Autowired
    private employeeservice service;

    @GetMapping("/employee/{id}")
    public Optional<employee> getemployeebyid(@PathVariable Long id){
        return service.getemployeebyid(id);
    }

    @GetMapping("/allemployees")
    public List<employee> getallemployees(){
        return service.getallemployees();
    }

    @PostMapping("/addemployee")
    public ResponseEntity<?> addemployee(@RequestBody employee employee){
        try{
            employee employee1=service.addemployee(employee);
            return new ResponseEntity<>(employee1, HttpStatus.CREATED);
        }catch(Exception e){
            return new ResponseEntity<>(e.getMessage(),HttpStatus.INTERNAL_SERVER_ERROR);
        }

    }
    @DeleteMapping("/deleteemployee/{id}")
    public void deleteemployeebyid(@PathVariable Long id){
        service.deleteemployee(id);

    }

    @PutMapping("/updateemployee/{id}")
    public ResponseEntity<?> updateemployeebyid(@PathVariable Long id,@RequestBody employee employee){
        return service.updateemployeebyid(id,employee);
    }

    @GetMapping("/filter/gender")
    public List<employee> filterbygender(@RequestParam String gender){
    return service.filterbygender(gender);
    }
    @GetMapping("/search")
    public List<employee> searchEmployees(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String email,
            @RequestParam(required = false) String phoneNumber
    ) {
        return service.searchEmployees(name, email, phoneNumber);
    }


}
