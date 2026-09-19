# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K4-L3A
**Thành viên:** Hồ Đình Tuấn Kiệt; Thành viên 2; Thành viên 3
**Ngày:** 2026-09-19

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
| `library-borrowing-student.md` | FixedSizeChunker (`fixed_size`) | 3 | 372.3 | Trung bình; có thể cắt giữa mục "Chính sách tại Thư viện UIT" nếu câu dài. |
| `library-borrowing-student.md` | SentenceChunker (`by_sentences`) | 4 | 254.2 | Khá tốt cho câu ngắn, nhưng không giữ heading đi kèm mọi chunk. |
| `library-borrowing-student.md` | RecursiveChunker (`recursive`) | 3 | 341.0 | Tốt; giữ đoạn/mục tốt hơn fixed-size. |
| `library-account-student.md` | FixedSizeChunker (`fixed_size`) | 3 | 366.7 | Trung bình; thông tin phí vẫn nằm cùng chunk nhưng heading có thể bị tách. |
| `library-account-student.md` | SentenceChunker (`by_sentences`) | 3 | 333.7 | Tốt với văn bản ngắn, nhưng dễ mất cấu trúc mục. |
| `library-account-student.md` | RecursiveChunker (`recursive`) | 3 | 335.3 | Tốt; ít chunk vụn. |
| `library-renewal-guide.md` | FixedSizeChunker (`fixed_size`) | 2 | 320.0 | Tạm ổn vì file ngắn. |
| `library-renewal-guide.md` | SentenceChunker (`by_sentences`) | 3 | 195.7 | Dễ đọc nhưng tách "Các bước gia hạn" và "Lưu ý" thành các mảnh nhỏ hơn. |
| `library-renewal-guide.md` | RecursiveChunker (`recursive`) | 2 | 296.5 | Tốt; giữ các đoạn gần nhau. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Fixed-size baseline**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn cho chủ đề này:** Dùng `FixedSizeChunker(chunk_size=350, overlap=50)` làm baseline đơn giản. Overlap giúp giảm rủi ro mất thông tin ở ranh giới chunk, nhưng chiến lược này không hiểu heading/mục của văn bản.

**Thành viên 2 — Recursive**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Dùng `RecursiveChunker(chunk_size=450)` để ưu tiên cắt theo đoạn trống, dòng mới, câu rồi mới tới từ. Chiến lược này phù hợp với văn bản quy định ngắn vì hạn chế chunk vụn và giữ ngữ cảnh tốt hơn fixed-size.

**Thành viên 3 — Heading/section**
- **Loại chiến lược:** Custom heading chunker
- **Mô tả & lý do chọn:** Dùng chiến lược chia theo heading Markdown `#`, `##`, `###`. Corpus Thư viện UIT đã được làm sạch theo mục như "Tên đăng nhập", "Cơ sở dữ liệu dùng chung", "Lưu ý", nên heading chunker giữ đúng đơn vị nghiệp vụ và đáp ứng ràng buộc có thành viên chunk theo tiêu đề/mục.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def chunk(self, text: str) -> list[str]:
        chunks, current = [], []
        for line in text.splitlines():
            if line.startswith("#") and current:
                chunks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            chunks.append("\n".join(current).strip())
        return [chunk for chunk in chunks if chunk]
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thành viên 1 | FixedSizeChunker, chunk_size=350, overlap=50 | 7 | Dễ triển khai, có overlap, chạy ổn với file ngắn. | Có failure case khi câu trả lời nằm sát ranh giới chunk hoặc heading bị tách khỏi nội dung. |
| Thành viên 2 | RecursiveChunker, chunk_size=450 | 8 | Giữ đoạn tự nhiên hơn, ít chunk vụn. | Vẫn chưa tận dụng hoàn toàn cấu trúc heading của tài liệu quy định. |
| Thành viên 3 | HeadingChunker | 9 | Giữ nguyên heading + nội dung mục, top-3 của 5/5 query đều chứa expected doc. | Nếu một mục quá dài thì cần thêm bước chia nhỏ bên trong section. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> HeadingChunker phù hợp nhất với corpus này vì tài liệu quy định thư viện đã được làm sạch theo từng mục rõ ràng. Với 5 benchmark query, chiến lược heading nạp 22 chunk và top-3 đều chứa tài liệu expected; đồng thời chunk đọc được như một mục hoàn chỉnh, dễ kiểm chứng gold answer.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên UIT được mượn giáo trình tại Thư viện UIT bao nhiêu cuốn trong bao lâu và được gia hạn mấy lần? | Sinh viên được mượn 5 cuốn giáo trình trong 90 ngày, được gia hạn 2 lần, mỗi lần 15 ngày. | `library-borrowing-student`, mục `Chính sách tại Thư viện UIT`; dùng `metadata_filter={"audience": "student"}`. |
| 2 | Sinh viên từ năm 2 trở đi muốn gia hạn quyền truy cập cơ sở dữ liệu dùng chung thì phí mỗi năm là bao nhiêu? | Sinh viên từ năm 2 trở đi cần gia hạn quyền truy cập với phí 25.000 đồng mỗi năm tại Thư viện Trung tâm. | `library-account-student`, mục `Cơ sở dữ liệu dùng chung`; cần `metadata_filter={"audience": "student"}` để tránh nhầm với giảng viên miễn phí. |
| 3 | Cán bộ giảng viên UIT truy cập cơ sở dữ liệu dùng chung có mất phí không? | Cán bộ - giảng viên được miễn phí quyền truy cập cơ sở dữ liệu dùng chung của Hệ thống Thư viện ĐHQG-HCM. | `library-account-faculty`, mục `Cơ sở dữ liệu dùng chung`; dùng `metadata_filter={"audience": "faculty"}`. |
| 4 | Thư viện UIT mở cửa thứ Bảy lúc mấy giờ và đóng cửa lúc mấy giờ? | Thứ Bảy, Thư viện UIT mở cửa lúc 08:00 và đóng cửa lúc 16:00. | `library-hours`, mục `Lịch phục vụ trong tuần`; dùng `metadata_filter={"audience": "all"}`. |
| 5 | Bạn đọc cần làm gì để gia hạn tài liệu và chỉ được gia hạn trước ngày hết hạn bao lâu? | Bạn đọc đăng nhập tài khoản, chọn tài liệu cần gia hạn, chọn Renew Marked, xác nhận Yes; chỉ được gia hạn sách trước ngày hết hạn 1 hoặc 2 ngày. | `library-renewal-guide`, mục `Các bước gia hạn` và `Lưu ý`; dùng `metadata_filter={"audience": "all"}`. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mượn giáo trình của sinh viên | HeadingChunker | Có | Top-1 là `library-borrowing-student` chunk 3, score 0.720. |
| 2 | Phí gia hạn CSDL của sinh viên năm 2 trở đi | HeadingChunker | Có | Top-1 là `library-account-student` chunk 4, score 0.685. |
| 3 | CSDL dùng chung của cán bộ giảng viên có mất phí không | HeadingChunker | Có | Top-1 là `library-account-faculty` chunk 4, score 0.639. |
| 4 | Giờ mở cửa thứ Bảy | HeadingChunker | Có | Top-1 là `library-hours` chunk 2, score 0.667. |
| 5 | Cách gia hạn và thời điểm được gia hạn | HeadingChunker | Có | Top-1 là `library-renewal-guide` chunk 3, mục `Lưu ý`, score 0.593. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có. Metadata filter hữu ích nhất ở câu 2 vì cùng chủ đề tài khoản/CSDL nhưng sinh viên năm 2 trở đi phải gia hạn 25.000 đồng/năm, còn cán bộ - giảng viên được miễn phí; nếu không lọc `audience=student`, hệ thống có thể trả nhầm chunk của giảng viên. Câu 1 cũng dùng `audience=student` để tập trung vào chính sách mượn dành cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> Metadata `audience` không chỉ để trang trí: khi tách riêng file sinh viên và giảng viên, filter mới thật sự giúp tránh câu trả lời sai. Heading chunking phù hợp với văn bản quy định vì mỗi mục thường chứa một ý nghiệp vụ hoàn chỉnh. Với benchmark hiện tại, top-3 của 5/5 câu đều chứa expected doc khi dùng chiến lược heading.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một corpus nhưng chiến lược chunking làm thay đổi độ dễ kiểm chứng của kết quả. Fixed-size có thể vẫn tìm đúng tài liệu nhưng chunk đôi khi thiếu heading, trong khi heading chunker trả về một mục trọn vẹn nên dễ đối chiếu gold answer hơn. Failure case chính của nhóm là nếu một mục heading quá dài, heading chunker sẽ tạo chunk lớn và cần thêm bước recursive bên trong section.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ giữ cách tách tài liệu theo `audience`, nhưng thêm nhiều câu hỏi A/B không filter so với có filter để đo rõ hơn tác dụng của metadata. Với chunking, nhóm sẽ thử chiến lược lai: chia theo heading trước, sau đó dùng RecursiveChunker cho section quá dài.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **38 / 40** |
