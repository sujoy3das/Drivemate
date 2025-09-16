# ☁️ Cloud Storage Web Application (Google Drive-like)

This document describes the complete specification for the cloud storage
web application, including architecture, features, database schema,
storage handling, and subscription model.

------------------------------------------------------------------------

## 🔹 Overview

A subscription-based cloud storage system where users can: - Create
accounts and manage files/folders.\
- Upload, preview, and download encrypted files.\
- Use up to **20GB free storage**.\
- Upgrade to paid subscription plans (100GB, 200GB, etc.) set by Admin.

------------------------------------------------------------------------

## 🔹 Tech Stack

-   **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5\
-   **Backend:** Python Flask\
-   **Database:** MySQL\
-   **Storage:** Local Disk / AWS S3 / MinIO (encrypted at rest)\
-   **Deployment:** VPS/Web hosting with SSL enabled

------------------------------------------------------------------------

## 🔹 Core Features

### User Features

-   Register, login, logout\
-   Manage files/folders (upload, delete, rename, move)\
-   File preview (images, audio, video, docs, text)\
-   Subscription management\
-   Storage usage indicator

### Admin Features

-   Create & manage subscription plans (size, price, duration)\
-   View user storage usage\
-   Manage payments & renewals

### Security

-   Files stored encrypted (AES)\
-   HTTPS for secure transmission\
-   Role-based access (user vs admin)\
-   Quota enforcement

------------------------------------------------------------------------

## 🔹 System Architecture

**Components:** - **Frontend (Browser):** UI built with HTML5, CSS, JS,
Bootstrap.\
- **Backend (Flask):** Authentication, File Management, Subscription,
Admin APIs.\
- **Database (MySQL):** Users, Plans, Subscriptions, Files, Folders,
Payments.\
- **Storage:** Encrypted file store (local/S3/MinIO).\
- **Security:** SSL, encryption, access control.

**Flow Example (File Upload):** 1. User uploads file → sent to Flask
API.\
2. Backend checks quota in MySQL.\
3. Encrypt file → save to storage → log metadata in DB.\
4. Update storage usage → respond success.

------------------------------------------------------------------------

## 🔹 Database Schema (MySQL)

### Users

-   id (PK)\
-   name\
-   email (unique)\
-   password_hash\
-   role (admin/user)\
-   plan_id (FK → Plans)\
-   used_storage (in MB/GB)

### Plans

-   id (PK)\
-   name (Free, 100GB, 200GB...)\
-   size_limit (GB)\
-   price\
-   duration (months)

### Subscriptions

-   id (PK)\
-   user_id (FK → Users)\
-   plan_id (FK → Plans)\
-   start_date\
-   end_date\
-   active (boolean)

### Files

-   id (PK)\
-   user_id (FK → Users)\
-   folder_id (FK → Folders)\
-   filename\
-   path (storage location)\
-   size\
-   mime_type\
-   encrypted_key (if per-file encryption)\
-   created_at

### Folders

-   id (PK)\
-   user_id (FK → Users)\
-   parent_id (FK → Folders, nullable)\
-   name

### Payments

-   id (PK)\
-   user_id (FK → Users)\
-   plan_id (FK → Plans)\
-   amount\
-   status (pending/success/failed)\
-   txn_id\
-   created_at

------------------------------------------------------------------------

## 🔹 File Preview Matrix

  --------------------------------------------------------------------------------
  **File Type**        **Preview         **Frontend            **Backend
                       Method**          Rendering**           Handling**
  -------------------- ----------------- --------------------- -------------------
  Images (JPG, PNG,    Direct view       `<img>`               Decrypt → stream
  GIF, WebP)                             modal/lightbox        

  Audio (MP3, WAV,     Audio player      `<audio>`             Decrypt → stream
  OGG)                                                         

  Video (MP4, WebM,    Video player      `<video>`             Chunked streaming
  MKV)                                                         

  PDF                  PDF viewer        `<iframe>` / PDF.js   Decrypt → stream

  Word (DOC, DOCX)     Convert to PDF    PDF.js                Convert → stream

  Excel (XLS, XLSX,    Convert to        DataTables.js         Convert server-side
  CSV)                 PDF/HTML                                

  PPT (PPT, PPTX)      Convert to        Slideshow viewer      Convert server-side
                       PDF/images                              

  Text/Markdown/Code   Text viewer       `<pre>` + Prism.js    Decrypt → return
                                                               text

  Compressed (ZIP,     File explorer     JS unzip viewer       Extract list
  RAR)                                                         server-side

  Others               No preview        "No preview           Allow download only
                                         available"            
  --------------------------------------------------------------------------------

------------------------------------------------------------------------

## 🔹 Deployment

-   VPS or web hosting with SSL (Let's Encrypt or similar).\
-   Flask served via Gunicorn + Nginx.\
-   Cron job for subscription expiry handling.

------------------------------------------------------------------------

## 🔹 Implementation Phases

**Phase 1 (MVP):**\
- User auth, free plan (20GB).\
- File upload, download, delete.\
- Basic previews (images, audio, video, text, PDF).

**Phase 2:**\
- Paid subscriptions (100GB, 200GB...).\
- Payment gateway integration (UPI/Stripe/Razorpay/PayPal).\
- Admin panel (plans, users, payments).

**Phase 3:**\
- Advanced previews (Word, Excel, PPT, ZIP).\
- File sharing with access control.\
- Activity logs & audit trail.

------------------------------------------------------------------------
