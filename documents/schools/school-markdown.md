# 🏫 School Academic Model Overview

This document explains the relationships between the core models that define academic offerings at schools using Django ORM. The model is designed to be flexible, allowing each `SchoolBranch` to offer multiple `Degrees`, `Colleges`, and `Majors` with specific configurations.

## 🧠 Core Models

- **EducationalLevel**: Represents the broad level of education (e.g., Primary, Secondary, Higher Education).
- **EducationDegree**: Tied to an educational level (e.g., Bachelor's, Master's).
- **College**: Represents faculties like Engineering, Business, etc. Linked to branches and degrees.
- **Major**: Fields of study (e.g., Computer Science), which can belong to colleges and be associated with degrees.

## 🏫 School + Branches

- **School**: The institution entity.
- **SchoolBranch**: Physical or virtual campuses under a school.

## 📦 Offer Models

These "join" models connect core academic data with schools and branches.

- **SchoolDegreeOffering**: Connects a School (and optionally Branch) to a Degree, including info like tuition, deadlines, etc.
- **SchoolCollegeAssociation**: Links schools/branches to colleges with extra context (e.g., partnership type, dual degrees).
- **SchoolMajorOffering**: Ties a major to a school/branch/degree with full enrollment data.

## 📑 Meta Requirements

- **DocumentRequirement**: Lists required docs per major.
- **CandidateQualification**: Stores expected GPA, English score, etc. for a major or degree.

## 🔗 Diagram of Relationships

```mermaid
graph TD
  subgraph Core Data
    EL[EducationalLevel]
    ED[EducationDegree]
    C[College]
    M[Major]
  end

  subgraph Schools
    SB[SchoolBranch]
    S[School]
  end

  subgraph Offerings
    SDO[SchoolDegreeOffering]
    SCA[SchoolCollegeAssociation]
    SMO[SchoolMajorOffering]
  end

  subgraph Meta
    DR[DocumentRequirement]
    CQ[CandidateQualification]
  end

  %% Core Relationships
  ED --> EL
  C --> ED
  M --> ED
  M --> C

  %% School Relationships
  C --> SB
  SDO --> S
  SDO --> ED
  SDO --> SB

  SCA --> S
  SCA --> C
  SCA --> SB

  SMO --> S
  SMO --> M
  SMO --> SB
  SMO --> ED

  DR --> M
  CQ --> M
  CQ --> ED
