# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và quy định Thư viện UIT

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề Thư viện UIT vì đây là dịch vụ/quy định đại học đúng ràng buộc K4-L3A, có nguồn công khai từ website chính thức của Thư viện UIT, và nội dung có nhiều con số để kiểm chứng như số lượng sách mượn, số ngày mượn, phí gia hạn CSDL, giờ phục vụ. Corpus cũng có nhiều `audience` khác nhau (`student`, `faculty`, `all`), nên có thể kiểm tra metadata filtering thật sự thay vì chỉ lọc hình thức.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Tài khoản Thư viện cho cán bộ giảng viên UIT | https://thuvien.uit.edu.vn/page/tai-khoan-thu-vien | 2026-09-19 / not-stated | 984 | `doc_id=library-account-faculty`; `audience=faculty`; `department=library`; `category=account`; `language=vi` |
| 2 | Tài khoản Thư viện cho sinh viên UIT | https://thuvien.uit.edu.vn/page/tai-khoan-thu-vien | 2026-09-19 / not-stated | 1010 | `doc_id=library-account-student`; `audience=student`; `department=library`; `category=account`; `language=vi` |
| 3 | Chính sách mượn tài liệu cho sinh viên UIT | https://thuvien.uit.edu.vn/page/chinh-sach-muon-tra-tai-lieu | 2026-09-19 / not-stated | 1027 | `doc_id=library-borrowing-student`; `audience=student`; `department=library`; `category=borrowing`; `language=vi` |
| 4 | Chính sách thẻ Thư viện UIT | https://thuvien.uit.edu.vn/page/chinh-sach-the-thu-vien | 2026-09-19 / not-stated | 1226 | `doc_id=library-card-services`; `audience=all`; `department=library`; `category=library-card`; `language=vi` |
| 5 | Thời gian phục vụ Thư viện UIT | https://thuvien.uit.edu.vn/page/thoi-gian-phuc-vu | 2026-09-19 / not-stated | 555 | `doc_id=library-hours`; `audience=all`; `department=library`; `category=opening-hours`; `language=vi` |
| 6 | Hướng dẫn gia hạn tài liệu Thư viện UIT | https://thuvien.uit.edu.vn/page/huong-dan-gia-han-tai-lieu | 2026-09-19 / not-stated | 595 | `doc_id=library-renewal-guide`; `audience=all`; `department=library`; `category=renewal`; `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `library-account-student` | Định danh ổn định cho tài liệu/chunk, giúp đối chiếu với `sources.csv` và gold answer. |
| `title` | string | `Tài khoản Thư viện cho sinh viên UIT` | Hiển thị tên tài liệu và giúp người đánh giá đọc kết quả retrieval nhanh hơn. |
| `source_url` | string URL | `https://thuvien.uit.edu.vn/page/tai-khoan-thu-vien` | Truy vết nguồn gốc để kiểm chứng câu trả lời. |
| `retrieved_at` | date string | `2026-09-19` | Ghi ngày lấy dữ liệu để biết độ mới của corpus. |
| `document_version` | string | `not-stated` | Ghi phiên bản/ngày hiệu lực nếu nguồn nêu rõ; với corpus này nguồn không nêu nên dùng `not-stated`. |
| `audience` | enum string | `student`, `faculty`, `all` | Trường lọc quan trọng nhất; dùng để tách câu trả lời của sinh viên và giảng viên. |
| `department` | string | `library` | Lọc theo đơn vị phụ trách khi corpus mở rộng sang học vụ, học phí, học bổng. |
| `category` | string | `account`, `borrowing`, `renewal` | Lọc theo nhóm nghiệp vụ/câu hỏi, giúp retrieval tập trung hơn. |
| `language` | string | `vi` | Lọc ngôn ngữ nếu sau này corpus có cả tiếng Việt và tiếng Anh. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
