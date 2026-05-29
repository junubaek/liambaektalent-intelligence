# LiamBaekTalent Database Comprehensive Health & Parsing Audit Report
*Generated at: 2026-05-29 | Database: `candidates.db`*

## 1. Executive Summary & Database Vital Signs

| Vital Metric | Value | Percentage of Total | Status / Assessment |
| :--- | :---: | :---: | :--- |
| **Total Candidates** | **3996명** | 100% | Primary Pool Size |
| Unparsable Resumes (Raw Text < 100 chars) | 1명 | 0.03% | Good (Blank or Scanned PDFs) |
| Empty Career JSON (`[]` or NULL) | 31명 | 0.78% | Good (Failed Career Extraction) |
| Empty Education JSON (`[]` or NULL) | 1078명 | 26.98% | Acceptable |
| Empty/Weak Profile Summaries | 175명 | 4.38% | Good |
| Non-Standard / Unmapped Sectors | 255명 | 6.38% | Requires Reclassification |


## 2. Granular Field Integrity Audit (Missing/Null Fields)
Analyzes columns that hold key contact information or metadata. A high missing percentage in contact information is standard for raw resumes, but metadata should be populated.

| Target Field | Missing/Null Count | Populated Count | Integrity Rate (%) |
| :--- | :---: | :---: | :---: |
| `email` | 1043명 | 2953명 | 73.90% |
| `phone` | 1196명 | 2800명 | 70.07% |
| `birth_year` | 2177명 | 1819명 | 45.52% |
| `current_company` | 431명 | 3565명 | 89.21% |
| `total_years` | 25명 | 3971명 | 99.37% |
| `profile_summary` | 174명 | 3822명 | 95.65% |
| `careers_json` | 30명 | 3966명 | 99.25% |
| `education_json` | 1077명 | 2919명 | 73.05% |
| `sector` | 158명 | 3838명 | 96.05% |
| `google_drive_url` | 316명 | 3680명 | 92.09% |


## 3. Detailed Analysis of Parsing Failures & Raw Text Anomalies

### 3.1 Unparsable / Scanned PDF Resumes (Raw Text < 100 Chars)
These candidates represent files where the PDF text extractor returned zero or extremely short text (typically due to image-only scanned files or extraction errors). These candidates **cannot be matched via semantic search (Vector) or lexical search (BM25)** because their text is empty.

| Candidate ID | Candidate Name | Raw Text Length (Bytes) | Sector | Action Needed |
| :--- | :--- | :---: | :--- | :--- |
| `32e22567-1b6f-8144-aa34-f1e2a5880c7c` | 김유성 | 24 | None | OCR/Manual Upload |


### 3.2 Empty Career Schemas with Populated Raw Text
These represent candidates where the original text exists, but the LLM parsing parser failed to structure them into the `careers_json` schema. These candidates **can match vector searches but will fail depth score calculations (Tower 4) or role-based graph searches (Tower 2)**.

| Candidate ID | Candidate Name | Raw Text Length (Chars) | Sector | Action Needed |
| :--- | :--- | :---: | :--- | :--- |
| `32e22567-1b6f-8127-9c55-c3e95da63767` | 김국도 | 10911 | Biotechnology | Trigger LLM Career Reparse |
| `32e22567-1b6f-81e1-b8fc-c946f1c6f5c4` | 정소윤 | 1928 | B2B영업 | Trigger LLM Career Reparse |
| `df93e3e8-6736-4324-8cac-d62fff832a86` | 황인선 | 22953 | SW | Trigger LLM Career Reparse |
| `332713ee-ae78-461a-8560-218774db09c8` | 고요셉 | 1009 | SW | Trigger LLM Career Reparse |
| `52caeda6-70ce-4d0e-b17b-d282dc7d0e5d` | 심초아 | 3881 | Marketing | Trigger LLM Career Reparse |
| `19ee4fad-95d9-4ca7-a704-cf10c4346efc` | 이진호 | 1731 | SW | Trigger LLM Career Reparse |
| `938098ba-c1a9-41b9-96ab-33fd94c1b886` | 김민준 | 2016 | SW | Trigger LLM Career Reparse |
| `772fc137-6af8-4151-aa58-da69be2b7898` | 유동준 | 15243 | Engineering | Trigger LLM Career Reparse |
| `fd855201-ecfc-4451-b3f5-c747436ba067` | 이유진 | 2798 | Quality Management | Trigger LLM Career Reparse |
| `325d7f5d-8e04-498a-bf28-020c62ad8ed1` | 이정호 | 41776 | SW | Trigger LLM Career Reparse |
| `a19a03b0-2e49-4dfe-9798-a1e2ab06c986` | 김용호 | 44650 | SW | Trigger LLM Career Reparse |
| `bcc7fdf5-ab02-4202-b737-dc12c967e7e3` | 현석준 | 21398 | Life Science R&D | Trigger LLM Career Reparse |


## 4. Sector Normalization Status

- **Standardized Sector Coverage**: **3741명** (93.62%)
- **Remaining Unmapped/Broken Sectors**: **255명** (6.38%)

### List of Remaining Non-Standard Candidates
| Candidate ID | Candidate Name | Current Stored Sector | Action |
| :--- | :--- | :--- | :--- |
| `32e22567-1b6f-8103-88ea-cb199dc22bd6` | 김인영 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-810a-94c5-e18603f63721` | 송승현 | `Electronics Engineering` | Re-classify to standard list |
| `32e22567-1b6f-811b-8d52-ef3711e796ca` | 박상준 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-8127-9c55-c3e95da63767` | 김국도 | `Biotechnology` | Re-classify to standard list |
| `32e22567-1b6f-812e-8dd2-f5db02162988` | 조영승 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-8133-9343-f16e8932d3a5` | 송경석 | `Financial_Accounting` | Re-classify to standard list |
| `32e22567-1b6f-8137-ab00-c5281436c797` | 김잔디 | `물류_Logistics` | Re-classify to standard list |
| `32e22567-1b6f-8147-9808-e593b90198da` | 장한별 | `Corporate_Strategic_Planning` | Re-classify to standard list |
| `32e22567-1b6f-8152-b888-cf4f6fcaca4f` | 공윤호 | `사업개발_BD` | Re-classify to standard list |
| `32e22567-1b6f-8155-8cc6-c630f1789b62` | 이석제 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-815a-bd2d-c2de6fa94300` | 박승수 | `사업개발_BD` | Re-classify to standard list |
| `32e22567-1b6f-815b-823f-fc726af60a11` | 김한미루 | `B2B영업` | Re-classify to standard list |
| `32e22567-1b6f-815c-9d7b-ebb8721cf9b3` | 정일석 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-8193-b6fc-d38224c8248a` | 한지훈 | `Supply Chain` | Re-classify to standard list |
| `32e22567-1b6f-8197-aa66-e5b08bad384a` | 이주형 | `물류_Logistics` | Re-classify to standard list |
| `32e22567-1b6f-81a6-860a-d84027b59667` | 허유리 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-81a9-9df2-d904e3d466ba` | 박규량 | `Manufacturing` | Re-classify to standard list |
| `32e22567-1b6f-81b0-b3fb-da1740d71bdc` | 송노겸 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-81b7-ae47-e9bf048f5353` | 이희진 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-81bc-a2ab-c03d0adc010d` | 박하선 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-81c5-afb6-f5eee57889de` | 양영환 | `Data_Engineering` | Re-classify to standard list |
| `32e22567-1b6f-81c7-9a20-dc8a8c238672` | 유홍열 | `Mechanical Engineering` | Re-classify to standard list |
| `32e22567-1b6f-81cd-8127-de5f8f792b0d` | 김율희 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-81cf-afca-c529a240a109` | 박수재 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-81d8-bb3e-e7fa99fee1fc` | 장한수 | `Manufacturing` | Re-classify to standard list |
| `32e22567-1b6f-81de-a5ed-f0dfec633282` | 유수현 | `SW` | Re-classify to standard list |
| `32e22567-1b6f-81e1-b8fc-c946f1c6f5c4` | 정소윤 | `B2B영업` | Re-classify to standard list |
| `32e22567-1b6f-81ef-80be-df9bb5420640` | 김준철 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-81f6-8c69-ea7bb48a8647` | 백수진 | `사업개발_BD` | Re-classify to standard list |
| `32022567-1b6f-8168-a7b8-ee2e63659012` | 신홍선 | `제공된 이력서 내용에서 특정 직군을 유추할 수 있는 정보가 부족하여 추출이 불가능합니다.` | Re-classify to standard list |

*...and 225 more candidates.* 
