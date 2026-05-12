package com.employee.employemgmt.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name="employees")
public class employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name="firstname")
    private String firstname;

    @Column(name="lastname")
    private String lastname;

    @Column(name="email",nullable=false,unique = true)
    private String email;
    @Column(name="gender")
    private String gender;

    @Column(name="age")
    private Integer age;

    @Column(name="joining_date")
    private LocalDate joiningDate;

    @Column(name="referred_by")
    private String referredBy;
    @Column(name="phone_number")
    private String phoneNumber;

    @Column(name="department")
    private String department;

    @Column(name="position")
    private String position;

    @Column(name="salary")
    private Double salary;

    @Column(name="address")
    private String address;

    @Column(name="city")
    private String city;

    @Column(name="state")
    private String state;

    @Column(name="country")
    private String country;

    @Column(name="status")
    private String status;


}
