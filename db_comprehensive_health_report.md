# LiamBaekTalent Database Comprehensive Health & Parsing Audit Report
*Generated at: 2026-05-29 | Database: `candidates.db`*

## 1. Executive Summary & Database Vital Signs

| Vital Metric | Value | Percentage of Total | Status / Assessment |
| :--- | :---: | :---: | :--- |
| **Total Candidates** | **3996명** | 100% | Primary Pool Size |
| Unparsable Resumes (Raw Text < 100 chars) | 48명 | 1.20% | Good (Blank or Scanned PDFs) |
| Empty Career JSON (`[]` or NULL) | 74명 | 1.85% | Good (Failed Career Extraction) |
| Empty Education JSON (`[]` or NULL) | 1119명 | 28.00% | Acceptable |
| Empty/Weak Profile Summaries | 214명 | 5.36% | Needs LLM Enrichment |
| Non-Standard / Unmapped Sectors | 219명 | 5.48% | Requires Reclassification |


## 2. Granular Field Integrity Audit (Missing/Null Fields)
Analyzes columns that hold key contact information or metadata. A high missing percentage in contact information is standard for raw resumes, but metadata should be populated.

| Target Field | Missing/Null Count | Populated Count | Integrity Rate (%) |
| :--- | :---: | :---: | :---: |
| `email` | 1043명 | 2953명 | 73.90% |
| `phone` | 1196명 | 2800명 | 70.07% |
| `birth_year` | 2177명 | 1819명 | 45.52% |
| `current_company` | 469명 | 3527명 | 88.26% |
| `total_years` | 63명 | 3933명 | 98.42% |
| `profile_summary` | 213명 | 3783명 | 94.67% |
| `careers_json` | 73명 | 3923명 | 98.17% |
| `education_json` | 1118명 | 2878명 | 72.02% |
| `sector` | 197명 | 3799명 | 95.07% |
| `google_drive_url` | 550명 | 3446명 | 86.24% |


## 3. Detailed Analysis of Parsing Failures & Raw Text Anomalies

### 3.1 Unparsable / Scanned PDF Resumes (Raw Text < 100 Chars)
These candidates represent files where the PDF text extractor returned zero or extremely short text (typically due to image-only scanned files or extraction errors). These candidates **cannot be matched via semantic search (Vector) or lexical search (BM25)** because their text is empty.

| Candidate ID | Candidate Name | Raw Text Length (Bytes) | Sector | Action Needed |
| :--- | :--- | :---: | :--- | :--- |
| `32e22567-1b6f-8103-88ea-cb199dc22bd6` | 김인영 | 21 | None | OCR/Manual Upload |
| `32e22567-1b6f-810a-94c5-e18603f63721` | 송승현 | 11 | None | OCR/Manual Upload |
| `32e22567-1b6f-811b-8d52-ef3711e796ca` | 박상준 | 19 | None | OCR/Manual Upload |
| `32e22567-1b6f-8121-bba0-d0d9925fff49` | 엄태우 | 32 | None | OCR/Manual Upload |
| `32e22567-1b6f-8127-9c55-c3e95da63767` | 김국도 | 27 | None | OCR/Manual Upload |
| `32e22567-1b6f-812a-be82-c3d8fc9f6fd8` | 이상민 | 22 | None | OCR/Manual Upload |
| `32e22567-1b6f-812e-8dd2-f5db02162988` | 조영승 | 26 | None | OCR/Manual Upload |
| `32e22567-1b6f-8133-9343-f16e8932d3a5` | 송경석 | 19 | None | OCR/Manual Upload |
| `32e22567-1b6f-8137-ab00-c5281436c797` | 김잔디 | 18 | None | OCR/Manual Upload |
| `32e22567-1b6f-813e-b2fd-fb3e7ed01d6b` | 김세영 | 12 | None | OCR/Manual Upload |


### 3.2 Empty Career Schemas with Populated Raw Text
These represent candidates where the original text exists, but the LLM parsing parser failed to structure them into the `careers_json` schema. These candidates **can match vector searches but will fail depth score calculations (Tower 4) or role-based graph searches (Tower 2)**.

| Candidate ID | Candidate Name | Raw Text Length (Chars) | Sector | Action Needed |
| :--- | :--- | :---: | :--- | :--- |
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

- **Standardized Sector Coverage**: **3777명** (94.52%)
- **Remaining Unmapped/Broken Sectors**: **219명** (5.48%)

### List of Remaining Non-Standard Candidates
| Candidate ID | Candidate Name | Current Stored Sector | Action |
| :--- | :--- | :--- | :--- |
| `32e22567-1b6f-81e1-b8fc-c946f1c6f5c4` | 정소윤 | `B2B영업` | Re-classify to standard list |
| `32022567-1b6f-8168-a7b8-ee2e63659012` | 신홍선 | `제공된 이력서 내용에서 특정 직군을 유추할 수 있는 정보가 부족하여 추출이 불가능합니다.` | Re-classify to standard list |
| `e262bbeb-df44-4a11-a702-e2a71c8be0a7` | 김현정 | `Product_Manager` | Re-classify to standard list |
| `df93e3e8-6736-4324-8cac-d62fff832a86` | 황인선 | `SW` | Re-classify to standard list |
| `332713ee-ae78-461a-8560-218774db09c8` | 고요셉 | `SW` | Re-classify to standard list |
| `e26dce75-3641-46e3-ade8-ef426000cd22` | 여정수 | `SW` | Re-classify to standard list |
| `01bba075-4acc-49fe-9444-2366f6ee1a7b` | 손태희 | `SW` | Re-classify to standard list |
| `19ee4fad-95d9-4ca7-a704-cf10c4346efc` | 이진호 | `SW` | Re-classify to standard list |
| `1d8f0081-06e8-4851-b239-a18b82f4e2db` | 김승현 | `B2B영업` | Re-classify to standard list |
| `7f061e1d-6523-4c55-958f-40158e70cccc` | 강은태 | `SW` | Re-classify to standard list |
| `938098ba-c1a9-41b9-96ab-33fd94c1b886` | 김민준 | `SW` | Re-classify to standard list |
| `6004cf18-e163-4735-a364-b8ce9ce19319` | 이민지 | `FinTech` | Re-classify to standard list |
| `76773431-0ace-4a68-96fc-2954daa6eb72` | 성장현 | `IT` | Re-classify to standard list |
| `7c5fed60-f81f-45b4-bba1-74f779f474d4` | 김희태 | `` | Re-classify to standard list |
| `9f1c353e-a74e-4c89-8249-606e97ddcc9b` | 손민정 | `Product_Manager` | Re-classify to standard list |
| `772fc137-6af8-4151-aa58-da69be2b7898` | 유동준 | `Engineering` | Re-classify to standard list |
| `fd855201-ecfc-4451-b3f5-c747436ba067` | 이유진 | `Quality Management` | Re-classify to standard list |
| `325d7f5d-8e04-498a-bf28-020c62ad8ed1` | 이정호 | `SW` | Re-classify to standard list |
| `b9297dec-38a9-42e8-b8e7-1000b27f8aa9` | 이정환 | `SW` | Re-classify to standard list |
| `003aac23-613c-4c4b-93b6-6ed1038c78f9` | 윤정민 | `` | Re-classify to standard list |
| `b67f2c64-08e4-43fe-a91f-cfe0d6622e16` | 장수빈 | `` | Re-classify to standard list |
| `a19a03b0-2e49-4dfe-9798-a1e2ab06c986` | 김용호 | `SW` | Re-classify to standard list |
| `61e7a76b-6252-446c-87fd-3e5ed1ab235e` | 김하영 | `Service_Planning` | Re-classify to standard list |
| `f0728481-bfd4-4d10-9aa3-afe3ad413c94` | 이정우 | `SW` | Re-classify to standard list |
| `fdf7dedd-5a2e-4e91-a6d3-73cf357d4463` | 조하준 | `사업개발_BD` | Re-classify to standard list |
| `bcc7fdf5-ab02-4202-b737-dc12c967e7e3` | 현석준 | `Life Science R&D` | Re-classify to standard list |
| `8ffb31e4-20ce-4904-bb76-e3bad468fe7f` | 신권철 | `FinTech` | Re-classify to standard list |
| `32e22567-1b6f-81fe-b3c5-fa5ce4a89e13` | 박진솔 | `` | Re-classify to standard list |
| `68c5d1e2-8169-47c0-912b-fb5fbcbf6f1c` | 김민아 | `General Business` | Re-classify to standard list |
| `bfd8a967-aa86-4558-a9ae-801939e93061` | 이력서 | `FinTech` | Re-classify to standard list |

*...and 189 more candidates.* 
