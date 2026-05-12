package com.employee.employemgmt.repository;

import com.employee.employemgmt.entity.employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface employeerepository extends JpaRepository<employee, Long> {

    boolean existsByEmail(String email);

    Optional<employee> findByEmail(String email);

    List<employee> findByPhoneNumber(String phoneNumber);

    List<employee> findByGenderIgnoreCase(String gender);

    @Query("""
    SELECT e FROM employee e
    WHERE
      LOWER(e.firstname) LIKE LOWER(CONCAT('%', :name, '%'))
      OR LOWER(e.lastname) LIKE LOWER(CONCAT('%', :name, '%'))
      OR LOWER(CONCAT(e.firstname, ' ', e.lastname)) LIKE LOWER(CONCAT('%', :name, '%'))
    """)
    List<employee> searchByName(@Param("name") String name);
}