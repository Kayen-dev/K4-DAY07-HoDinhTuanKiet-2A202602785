# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** ABCD — Lớp 3A, phòng E402
**Thành viên và phân vai:**

| Vai | Họ và tên | MSSV | Việc | Chiến lược chunking |
|---|---|---|---|---|
| **R1 · Data** | Huỳnh Tấn Trung | 2A202602742 | Chốt chủ đề, chia mỗi người 2–3 URL, kiểm metadata từng file, giữ `sources.csv` | `FixedSizeChunker(500, overlap=50)` |
| **R2 · Benchmark** | Nguyễn Tuấn Thành | 2A202602640 | Viết 5 query + gold answer, tự kiểm mỗi gold answer trích được từ tài liệu thật | `RecursiveChunker(500)` |
| **R3 · Strategy** | Nguyễn Trần Kiên | 2A202602571 | Bảo đảm không ai trùng chiến lược, **nhận vai chunk theo heading**, chạy baseline cho nhóm | `HeadingChunker(500)` |
| **Report & Demo Lead** | Hồ Đình Tuấn Kiệt | 2A202602785 | Gom kết quả cả nhóm, dẫn phần thuyết trình | `SentenceChunker(3)` |
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định mượn – trả tài liệu của thư viện đại học (thư mục `data/thu-vien/`, 9 tài liệu từ 4 trường).

**Tại sao nhóm chọn chủ đề này?**
> Quy định thư viện là loại văn bản mà **cùng một câu hỏi có nhiều đáp án đúng tuỳ đối tượng**: cùng câu "được mượn bao nhiêu ngày" thì sinh viên HUIT là 10 ngày còn giảng viên HUIT là 180 ngày. Đây đúng là tình huống mà `metadata_filter={"audience": "student"}` phải có việc thật, chứ không phải metadata đẹp trên giấy. Ngoài ra văn bản quy định có cấu trúc điều/mục rõ ràng nên phù hợp cho chiến lược chunk theo heading mà K4-L3A bắt buộc phải có một người thử.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu (`doc_id`) | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `huit-han-muc-muon-sinh-vien` | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / `not-stated` | 978 | audience=student, department=library, category=borrowing, language=vi, institution=huit |
| 2 | `huit-han-muc-muon-giang-vien` | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / `not-stated` | 963 | audience=faculty, department=library, category=borrowing, language=vi, institution=huit |
| 3 | `huit-doi-tuong-phuc-vu-va-nguoi-ngoai-truong` | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / `not-stated` | 841 | audience=all, department=library, category=eligibility, language=vi, institution=huit |
| 4 | `ptit-muon-ve-nha-sinh-vien` | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV ngày 14/10/2009 | 1384 | audience=student, department=library, category=borrowing, language=vi, institution=ptit |
| 5 | `ptit-muon-ve-nha-can-bo-giang-vien` | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV ngày 14/10/2009 | 762 | audience=faculty, department=library, category=borrowing, language=vi, institution=ptit |
| 6 | `ptit-quy-dinh-chung-va-xu-ly-vi-pham` | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV ngày 14/10/2009 | 2038 | audience=all, department=library, category=rules-and-penalties, language=vi, institution=ptit |
| 7 | `ut-muon-tra-sinh-vien` | https://lic.ut.edu.vn/quy-dinh-muon-tra-tai-lieu/ | 2026-09-19 / 2022-06-18 | 1292 | audience=student, department=library, category=borrowing, language=vi, institution=uth |
| 8 | `ut-muon-tra-can-bo-giang-vien` | https://lic.ut.edu.vn/quy-dinh-muon-tra-tai-lieu/ | 2026-09-19 / 2022-06-18 | 994 | audience=faculty, department=library, category=borrowing, language=vi, institution=uth |
| 9 | `ctu-the-va-muon-tra-sinh-vien` | https://lrc.ctu.edu.vn/index.php/manual-policy/96-sa-da-ng/231-cau-h-i-s-d-ng-trung-tam-h-c-li-u | 2026-09-19 / 2019-05-17 | 1069 | audience=student, department=learning-resource-center, category=borrowing, language=vi, institution=ctu |

**Kết quả checklist CP2** (`docs/DATA_COLLECTION.md` mục 6): 9/9 file `OK`, số file 9 (cần 5–10), `sources.csv` **khớp** 1-1, `audience = {student: 4, faculty: 3, all: 2}` → 3 giá trị khác nhau.

**Tách file theo `audience`:** trang HUIT và trang PTIT gộp hạn mức của sinh viên và của giảng viên trong **cùng một văn bản**. Nếu lưu nguyên thành một file `audience: all` thì `metadata_filter={"audience":"student"}` không lọc được gì — hai đáp án nằm chung một tài liệu. Nhóm tách mỗi trang thành các file theo đối tượng (chi tiết trong `data/thu-vien/PROVENANCE.txt` mục 3).

**Corpus mở rộng (CP6):** thêm `data/thu-vien-mo-rong/` — **10 tài liệu** từ ĐH Giao thông vận tải (`lib.utc.edu.vn`, QĐ 2706/QĐ-ĐHGTVT ngày 24/12/2019) và các trang bổ sung của UTH, ĐHCT, PTIT. Để riêng thư mục để **không phá checklist CP2** (yêu cầu 5–10 file) và để có số liệu so sánh corpus nhỏ (9 file / 33 chunk) với corpus lớn (19 file / 81 chunk). Chi tiết robots.txt và nguồn bị loại đợt 2 trong `data/thu-vien-mo-rong/PROVENANCE.txt`.

**Nguồn đã loại và lý do** (minh bạch nguồn):

| Nguồn | Lý do loại |
|-------|-----------|
| `lib.hcmut.edu.vn` | `/robots.txt` trả về trang HTML, không xác minh được quyền truy cập tự động |
| `www.vnulib.edu.vn` | `SSL: CERTIFICATE_VERIFY_FAILED` khi đọc robots.txt → không xác minh được |
| `lic.huc.edu.vn` | Nội dung trả về đã bị dịch/không còn số liệu gốc |
| `dav.edu.vn` | robots.txt trỏ sitemap sang domain lạ (`hhcorp.online`) |
| `lic.ut.edu.vn/noi-quy-thu-vien/` | Mâu thuẫn số liệu với trang chuyên đề cùng trường (45 ngày / 8 cuốn / phạt 1.000đ so với 1 học kỳ / 5+3 cuốn / phạt 500đ) → chọn trang chuyên đề làm nguồn chuẩn để gold answer không nhập nhằng |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. robots.txt của cả 4 domain đã được kiểm trước khi lấy (`lic.ut.edu.vn`, `lib.ptit.edu.vn`, `lrc.ctu.edu.vn` cho phép; `thuvien.huit.edu.vn` không có robots.txt → allow-all theo RFC 9309).
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. Trang HUIT không nêu số hiệu/ngày ban hành nên ghi `not-stated`, **không bịa số hiệu**.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum: student / faculty / staff / all | `student` | Trường lọc chính. Cùng một câu hỏi "mượn được bao nhiêu ngày" có đáp án khác nhau theo đối tượng; không lọc thì chunk của giảng viên (180 ngày) chiếm slot top-k của câu hỏi sinh viên (10 ngày). |
| `institution` | enum: huit / ptit / uth / ctu | `huit` | Corpus gộp 4 trường có quy định khác nhau. Lọc theo trường để so sánh, hoặc để trả lời câu hỏi chỉ về một trường mà không trộn số liệu trường khác. |
| `category` | enum: borrowing / rules-and-penalties / eligibility | `borrowing` | Tách câu hỏi về hạn mức mượn khỏi câu hỏi về phạt/điều kiện làm thẻ, giảm nhiễu khi query chung chung. |
| `department` | string | `library` | Chiều mở rộng khi corpus thêm mảng khác (học phí, ký túc xá); hiện tại phân biệt `library` với `learning-resource-center` của ĐHCT. |
| `language` | ISO 639-1 | `vi` | Chặn lẫn tài liệu tiếng Anh khi corpus mở rộng; embedding đa ngữ vẫn trả kết quả chéo ngôn ngữ nếu không lọc. |
| `document_version` | string hoặc `not-stated` | `817/QĐ-TTTV ngày 14/10/2009` | Truy vết phiên bản quy định trong câu trả lời (Source Traceability); phân biệt quy định cũ/mới khi cùng một trường có nhiều bản. |
| `source_url` / `retrieved_at` | URL / `YYYY-MM-DD` | `2026-09-19` | Provenance bắt buộc; agent trích dẫn được nguồn và người đọc kiểm chứng lại được. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

> **Cách nhóm so sánh:** bốn chiến lược được chạy trong **cùng một lượt `python bench.py`** trên cùng corpus, cùng 5 query, cùng embedding và cùng `top_k` (mục B của `ket_qua_benchmark.txt`). Làm vậy để loại hết biến số ngoài chiến lược chunking — nếu mỗi người chạy trên máy mình với cấu hình khác nhau thì con số không so được với nhau.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu, **đã bỏ frontmatter** trước khi so sánh (nếu không thì đang đo cả khối YAML chứ không phải nội dung quy định). Cột `heading` là chiến lược riêng `HeadingChunker`, không nằm trong comparator.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `ptit-quy-dinh-chung-va-xu-ly-vi-pham` (2038 ký tự) | FixedSizeChunker (`fixed_size`) | 5 | 447.6 | Kém — cắt giữa Điều 15 và Điều 17, một chunk chứa nửa điều này nửa điều kia |
| | SentenceChunker (`by_sentences`) | 8 | 252.5 | Trung bình — câu trọn vẹn nhưng mất ranh giới điều khoản |
| | RecursiveChunker (`recursive`) | 5 | 406.0 | Khá — ưu tiên cắt ở `\n\n` nên phần lớn trùng ranh giới đoạn |
| | **HeadingChunker** (`heading`) | **15** | **133.9** | **Tốt nhất — mỗi `Điều N.` thành một chunk độc lập, đúng đơn vị mà người soạn đã chia** |
| `ptit-muon-ve-nha-sinh-vien` (1384 ký tự) | FixedSizeChunker | 3 | 494.7 | Kém — bảng số liệu bị cắt ngang |
| | SentenceChunker | 5 | 274.8 | Trung bình — gạch đầu dòng không phải "câu" nên gom lệch |
| | RecursiveChunker | 3 | 460.0 | Khá |
| | **HeadingChunker** | **6** | **235.0** | **Tốt — "phòng mượn" và "phòng đọc kho mở" tách hẳn nhau, không lẫn hai bộ số liệu** |
| `ut-muon-tra-sinh-vien` (1292 ký tự) | FixedSizeChunker | 3 | 464.0 | Kém |
| | SentenceChunker | 5 | 257.0 | Trung bình |
| | RecursiveChunker | 3 | 429.3 | Khá |
| | **HeadingChunker** | **6** | **212.8** | **Tốt — mục "Xử lý vi phạm" tách khỏi mục "Số lượng được mượn"** |

Nhận xét: `HeadingChunker` cho số chunk gấp 2–3 lần và độ dài trung bình nhỏ hơn hẳn. Với văn bản thường thì chunk ngắn là nhược điểm (mất ngữ cảnh), nhưng với **văn bản quy định** thì ngược lại: mỗi điều/mục vốn đã tự chứa đủ nghĩa, nên chunk ngắn mà đúng ranh giới lại **tăng độ chính xác** — top-k không bị một chunk 500 ký tự gồm ba điều khoản khác nhau chiếm chỗ.

### Chiến lược của từng thành viên

Bốn chiến lược **không trùng nhau**, đúng ràng buộc của K4-L3A, và vai R3 nhận chunker theo heading như yêu cầu bắt buộc.

**R3 · Strategy — Nguyễn Trần Kiên (2A202602571)**
- **Loại chiến lược:** custom — `HeadingChunker`, fallback `RecursiveChunker` cho section dài
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy định đã được **người soạn** chia theo mục (`## Mượn về nhà tại phòng mượn (Điều 22)`, `**Điều 26.**`), mỗi mục là một đơn vị ngữ nghĩa trọn vẹn — cắt theo ranh giới đó là tận dụng lao động biên soạn sẵn có thay vì cắt mù theo số ký tự. Section nào dài quá ngưỡng thì hạ xuống recursive, và **gắn lại tiêu đề vào từng mảnh con**: không có bước này, mảnh thứ hai trở đi mất ngữ cảnh "đây là mục nói về cái gì". Sau CP6 bổ sung thêm một luật: **bỏ section chỉ có tiêu đề, không có thân** — chúng không mang thông tin nhưng lại lặp nhiều từ khoá nên thường cướp slot top-k của chunk thật sự chứa đáp án.
- **Code snippet (custom):** đầy đủ trong `src/heading_chunker.py`

```python
class HeadingChunker:
    # Heading markdown (# .. ######) hoac dong dang "Dieu 12." / "Điều 12."
    HEADING_PATTERN = re.compile(r"^(?:#{1,6}\s+\S.*|\**\s*(?:Điều|Dieu)\s+\d+\..*)$")

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        chunks = []
        sections = self._sections(text)
        has_body = any(body.strip() for _, body in sections)
        for heading, body in sections:
            section = f"{heading}\n{body}".strip() if heading else body
            if not section:
                continue
            # chunk chi co tieu de, khong co than -> bo di (failure case so 1)
            if heading and not body.strip() and has_body:
                continue
            if len(section) <= self.chunk_size:      # section vua kich thuoc
                chunks.append(section)
                continue
            # section qua dai -> ha xuong recursive, GAN LAI heading vao tung manh con
            prefix = f"{heading}\n" if (heading and self.keep_heading_in_subchunks) else ""
            budget = max(1, self.chunk_size - len(prefix))
            for piece in RecursiveChunker(chunk_size=budget).chunk(body or section):
                chunks.append(f"{prefix}{piece}".strip())
        return [c for c in chunks if c.strip()]
```

**R1 · Data — Huỳnh Tấn Trung (2A202602742)**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
- **Mô tả & lý do chọn:** Đường cơ sở đơn giản nhất, số chunk dự đoán được, và là chiến lược duy nhất có **overlap** — nhờ đó một thông tin nằm vắt ngang ranh giới cắt vẫn có hai cơ hội lọt top-k. Với corpus quy định thì nhược điểm rõ: nó cắt ngang bảng số liệu, một chunk có thể chứa cột "Đối tượng" mà mất cột "Số ngày".

**R2 · Benchmark — Nguyễn Tuấn Thành (2A202602640)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn:** Ưu tiên cắt ở ranh giới "to" (`\n\n` → `\n` → `. ` → ` `) nên phần lớn đường cắt trùng ranh giới đoạn, giữ được ngữ nghĩa mà không cần file có heading chuẩn. Đây cũng là chiến lược **chuyển được sang chủ đề khác** dễ nhất, nên nhóm giữ nó làm đường tham chiếu.

**Report & Demo Lead — Hồ Đình Tuấn Kiệt (2A202602785)**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Câu luôn trọn vẹn, hợp với văn xuôi. Nhóm cố ý để một người thử nó trên corpus quy định để thấy giới hạn: văn bản quy định viết bằng **gạch đầu dòng và bảng**, không phải câu văn xuôi, nên "câu" là đơn vị sai — chunker này gom lệch ở đúng những chỗ có số liệu.

### So Sánh Giữa Các Thành Viên

Cùng corpus `data/thu-vien/`, cùng 5 query, cùng `text-embedding-3-small`, cùng `top_k=5` — chỉ khác chiến lược chunking. Cột "điểm truy xuất" lấy trực tiếp từ mục B của `ket_qua_benchmark.txt` (chấm riêng phần retrieval, thang 10).

| Thành viên | Chiến lược | Số chunk (avg ký tự) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|-----------|----------|----------------------|-----------|----------|
| Kiên (R3) | **HeadingChunker** | 33 (235.8) | **10** | Chunk trùng ranh giới điều/mục; chunk nào cũng mang tiêu đề nên đọc lên biết ngay thuộc mục gì; tách sạch "phòng mượn" khỏi "phòng đọc kho mở" | Chunk ngắn (trung bình 235.8 ký tự) nên **bắt buộc chạy `top_k` ≥ 5**; câu hỏi trải qua nhiều mục sẽ cần `top_k` lớn hơn; phụ thuộc vào việc file có heading chuẩn |
| Thành (R2) | RecursiveChunker | 26 (395.7) | 9 | Chunk to, ít, ngữ cảnh rộng; không cần file có heading | Một chunk có thể gộp cả hạn mức lẫn chế tài, retrieval trả về đúng file nhưng sai mục |
| Trung (R1) | FixedSizeChunker (overlap 50) | 27 (415.6) | **10** | Đơn giản nhất, số chunk dự đoán được, có overlap nên thông tin vắt ngang ranh giới vẫn được cứu | Cắt ngang bảng số liệu và ngang giữa hai điều khoản; chunk đọc lên không biết thuộc mục nào |
| Kiệt (Report/Demo) | SentenceChunker | 34 (301.7) | **10** | Câu luôn trọn vẹn, không bao giờ cắt giữa câu | Văn bản quy định viết bằng gạch đầu dòng và bảng, không phải câu văn xuôi, nên "câu" là đơn vị sai — với `MockEmbedder` nó tụt xuống 4/10, thấp nhất nhóm |

### CP6 — Chấm lại bằng hai mức, kết luận bị lật ngược

Bảng trên chấm theo **chất lượng ranh giới chunk đọc bằng mắt**. Khi chấm lại bằng thang hai mức của `docs/SCORING.md` (`python bench.py`, mục B), kết quả khác hẳn:

**Cấu hình chính thức:** `text-embedding-3-small` + `gpt-4o-mini`, `HeadingChunker(500)`, `top_k=5`, 9 file → **33 chunk**.

| Chiến lược | Số chunk | Độ dài TB | Cách chấm ngây thơ (gold `doc_id` trong top-5) | Chấm hai mức (chỉ retrieval) |
|---|---|---|---|---|
| heading | 33 | 235.8 | 5/5 | **10/10** |
| recursive | 26 | 395.7 | 5/5 | 9/10 |
| fixed_size | 27 | 415.6 | 5/5 | **10/10** |
| by_sentences | 34 | 301.7 | 5/5 | **10/10** |

> Bảng này chấm **riêng phần retrieval**, không tính mức 3 (guardrail chặn agent), vì mục đích là so sánh chiến lược chunking. Vì vậy `heading` đạt 10/10 ở đây nhưng tổng ở mục 3 chỉ 9/10 — câu 5 bị guardrail `ambiguous` chặn.

**Đối chiếu với `MockEmbedder`** (lý do bắt buộc phải đổi sang embedding thật):

| Chiến lược | doc-hit | Chấm hai mức |
|---|---|---|
| heading | **5/5** | **6/10** |
| recursive | 4/5 | 7/10 |
| fixed_size | 4/5 | 6/10 |
| by_sentences | **5/5** | **4/10** |

Với mock, hai chiến lược có `doc-hit` **đẹp nhất** (5/5) lại có điểm nội dung **thấp nhất và thấp nhì** — chênh 6 bậc. Với embedding thật, cả bốn chiến lược đều 5/5 doc-hit và 9–10/10 điểm nội dung: khoảng cách gần như biến mất.

**`top_k` quan trọng hơn chiến lược chunking.** Cùng cấu hình, chỉ đổi `top_k` từ 3 lên 5:

| | `top_k=3` | `top_k=5` |
|---|---|---|
| heading (mục A) | 8/10 | **9/10** |
| heading (chỉ retrieval) | 8/10 | **10/10** |
| Câu 5 | 0/2 — chunk chứa `gấp 03 lần` nằm ngoài top-3 | 1/2 — chunk đó lên hạng 4 |

`HeadingChunker` cho chunk trung bình chỉ 235 ký tự, nên 3 slot không đủ chứa đủ thông tin. Chunk càng ngắn thì `top_k` phải càng lớn — đây là quan hệ đánh đổi mà bảng so sánh chiến lược một mình không cho thấy.

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Ở cấu hình cuối, **`heading`, `fixed_size` và `by_sentences` đều 10/10**, `recursive` 9/10, cả bốn 5/5 doc-hit. Kết luận trung thực là **ở corpus nhỏ và sạch như thế này, chiến lược chunking không phải yếu tố quyết định**. Ba thứ khác quyết định nhiều hơn, xếp theo mức ảnh hưởng đo được:
> 1. **Embedding** — đổi mock sang model thật nâng từ 6/10 lên 9/10, không đổi một dòng chunking nào.
> 2. **`top_k`** — chỉ đổi 3 → 5 nâng `heading` từ 8/10 lên 10/10 (retrieval).
> 3. **Bộ lọc metadata** — không lọc thì câu 1 rơi từ 2/2 xuống 0/2 ở cả ba chiến lược.
>
> `HeadingChunker` vẫn là lựa chọn tôi giữ, vì đơn vị truy xuất tự nhiên của văn bản quy định là **điều/mục**: chunk nào đọc lên cũng biết ngay thuộc mục gì, và khi corpus phình lên 19 file thì nó không tụt điểm. Nhưng nó có ràng buộc đi kèm: chunk trung bình chỉ 235 ký tự nên **phải chạy với `top_k` ≥ 5**. Kết luận "chunk ngắn đẹp hơn" chỉ đúng khi nói kèm `top_k` — hai tham số này không tách rời được. Khi người dùng hỏi "làm mất sách thì đền thế nào", thứ họ cần là trọn mục "Xử lý vi phạm" — không phải nửa mục đó dính thêm nửa mục "Số lượng được mượn". Bảng Baseline cho thấy điều này bằng số: cùng file PTIT 2038 ký tự, fixed-size ra 5 chunk trung bình 447 ký tự (mỗi chunk gộp 3–4 điều), còn heading ra 15 chunk trung bình 134 ký tự — đúng 15 điều khoản riêng biệt.
> Điều quan trọng cần nói thẳng: ở cấu hình `MockEmbedder`, **khác biệt giữa các chiến lược chunking gần như không đo được bằng điểm số**, vì mock băm MD5 và không có ngữ nghĩa. Cột "điểm truy xuất" ở trên là đánh giá theo *chất lượng ranh giới chunk* (đọc và kiểm bằng mắt từng chunk), không phải theo score. Muốn có số liệu so sánh thật thì phải chạy lại với `EMBEDDING_PROVIDER=local` hoặc `gemini`.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

Bộ câu hỏi nằm trong `BENCHMARK_QUERIES` của `bench.py`; kết quả đầy đủ trong `ket_qua_benchmark.txt`.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thư viện cho mượn tài liệu về nhà tối đa bao nhiêu ngày và được gia hạn thế nào? *(tra số liệu — **cần** `metadata_filter={"audience":"student"}`)* | Sinh viên, học viên HUIT: 3 tài liệu, thời hạn **10 ngày**, được gia hạn **1 lần thêm 10 ngày**. | `huit-han-muc-muon-sinh-vien#0` (mục "Số lượng và thời hạn mượn") |
| 2 | Người ngoài trường muốn sử dụng thư viện thì cần giấy tờ gì và được mượn bao nhiêu tài liệu? *(hỏi điều kiện)* | Phải có **giấy giới thiệu của cơ quan chủ quản kèm Chứng minh thư**; được mượn **1 tài liệu, 10 ngày, không gia hạn**. | `huit-doi-tuong-phuc-vu-va-nguoi-ngoai-truong#1` (đối tượng) + `#2` (hạn mức 1 tài liệu / 10 ngày) |
| 3 | Sinh viên hệ chính quy được mượn tối đa bao nhiêu cuốn ở phòng mượn và thời hạn bao lâu? *(tra số liệu)* | Tối đa **08 cuốn**, thời hạn **01 học kỳ (150 ngày)**. | `ptit-muon-ve-nha-sinh-vien#1` (Điều 22) |
| 4 | Giữ tài liệu quá hạn thì bị xử lý theo những mức nào? *(liệt kê)* | 1–30 ngày: nhắc nhở. 31–60 ngày: khoá tài khoản 1 tháng. Từ 61 ngày: gửi thông báo vi phạm đến đơn vị quản lý. | `ctu-the-va-muon-tra-sinh-vien#5` (mục "Xử lý giữ tài liệu quá hạn") |
| 5 | Làm mất tài liệu của thư viện thì bồi thường như thế nào? *(hỏi quy trình / chế tài)* | Bồi thường bằng tài liệu **cùng nhan đề, cùng tác giả** + lệ phí thẻ từ **10.000đ**; nếu không tìm được tài liệu tương tự thì bồi thường tiền mặt **gấp 03 lần** giá trị + **10.000đ**. | `ut-muon-tra-sinh-vien#5` / `ut-muon-tra-can-bo-giang-vien#4` (mục "Xử lý vi phạm") |

**Vì sao câu 1 buộc phải lọc `audience`:** corpus có hai tài liệu **cùng chủ đề, cùng từ vựng, cùng trường**, chỉ khác đối tượng và khác đáp án — `huit-han-muc-muon-sinh-vien` (10 ngày) và `huit-han-muc-muon-giang-vien` (180 ngày). Câu hỏi cố tình **không nêu người hỏi là ai**. Không lọc thì retrieval lẫn hai tài liệu và agent trả lời sai đối tượng; `institution` thu hẹp về HUIT nhưng **chính `audience` mới là chiều quyết định 10 hay 180**.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

Cấu hình: `HeadingChunker(chunk_size=500)`, `MockEmbedder`, `top_k=3`, 9 file → 54 chunk.

Chạy với `text-embedding-3-small` + `gpt-4o-mini`, `HeadingChunker(500)`, `top_k=5`:

| # | Câu hỏi | Gold trong top-5? | Agent trả lời? | Ghi chú | Điểm |
|---|---------|---|---|---------|------|
| 1 | Hạn mức mượn (ẩn đối tượng) | hạng 1 | Có | *"tối đa **10 ngày**, gia hạn **1 lần** thêm **10 ngày** [2]"* | **2** |
| 2 | Người ngoài trường | hạng 1 | Có | Trả lời phần giấy tờ kèm `[1]`, **nói thẳng** phần số lượng không có trong ngữ cảnh | **2** |
| 3 | SV chính quy PTIT, phòng mượn | hạng 1 | Có | *"**08 cuốn**, **01 học kỳ (150 ngày)** [1]"* | **2** |
| 4 | Các mức xử lý quá hạn (ĐHCT) | hạng 1 | Có | Liệt kê đủ ba mức kèm trích dẫn | **2** |
| 5 | Bồi thường khi làm mất | hạng 1 | **Không** (`ambiguous`) | Retrieval đúng, guardrail chặn — xem phân tích lỗi | 1 |
| | | | | **Tổng** | **9 / 10** |

Câu 2 đáng chú ý: ngữ cảnh chỉ có phần "giấy giới thiệu", không có bảng hạn mức 1 tài liệu/10 ngày. LLM trả lời phần có và **nói rõ phần còn lại không tìm thấy trong tài liệu**, thay vì bịa. Đây là ràng buộc chống bịa trong prompt hoạt động đúng trên dữ liệu thật.

**Với `MockEmbedder` (đối chiếu):** tổng chỉ **6/10**.

### CP6 — Chấm hai mức: chênh lệch với cách chấm ngây thơ

Cách chấm ngây thơ (chỉ kiểm `doc_id` gold có trong top-3) cho **5/5**. Chấm theo `docs/SCORING.md` — top-3 phải có chunk liên quan **và** ngữ cảnh phải trả lời được — cho **6/10**. `bench.py` khai báo cho mỗi câu một chuỗi đặc trưng `must_contain` và kiểm chuỗi đó có thật trong ngữ cảnh truy xuất được hay không:

Hàm chấm có **ba mức**, chặt dần:

- **Mức 1** — gold `doc_id` có trong top-k (cách chấm ngây thơ).
- **Mức 2** — chuỗi `must_contain` có trong ngữ cảnh, **và phải nằm trong chunk thuộc gold doc**. Không có ràng buộc sau, hai điều kiện có thể được thoả bởi **hai tài liệu khác nhau**: gold doc lên hạng 1 bằng một section không chứa đáp án, còn đáp án đến từ file khác.
- **Mức 3** — agent có thực sự trả lời không. `docs/SCORING.md` đòi "top-3 có chunk liên quan **và agent trả lời đúng**"; guardrail chặn thì người dùng không nhận được gì, không thể cho điểm tối đa.

**Số chính thức** (`text-embedding-3-small`, `top_k=5`):

| # | `must_contain` | Mức 1 | Mức 2 (trong gold doc) | Mức 3 (agent) | best score | Điểm |
|---|---|---|---|---|---|---|
| 1 | `10 ngày` | hạng 1 | Có | Có | +0.7348 | **2** |
| 2 | `giấy giới thiệu` | hạng 1 | Có | Có | +0.5614 | **2** |
| 3 | `150 ngày` | hạng 1 | Có | Có | +0.6431 | **2** |
| 4 | `khoá tài khoản` | hạng 1 | Có | Có | +0.6612 | **2** |
| 5 | `gấp 03 lần` | hạng 1 | Có | **Không (`ambiguous`)** | +0.5748 | **1** |

Ngây thơ **5/5** · ba mức **9/10**.

Câu 5 là ca duy nhất mất điểm, và mất vì **guardrail**, không vì retrieval: top-1 và top-2 là mục "Quy định chung" của hai file sinh viên/giảng viên UTH — hai đoạn gần như trùng nhau, chênh 0.0083 điểm, dưới `RAG_MARGIN=0.02`. Agent thấy top-k trải trên hai `audience` nên hỏi ngược thay vì trả lời. Trong trường hợp này mức bồi thường của hai nhóm **giống hệt nhau** nên việc hỏi lại là thừa — đây là đánh đổi precision/recall của guardrail, xem phân tích lỗi ở mục 2.

**Với `MockEmbedder` (đối chiếu):** ngây thơ **5/5**, ba mức **6/10**. Câu 1 khi đó được **0 điểm dù gold ở hạng 1**: cả ba chunk top-3 đều thuộc đúng file, nhưng chunk chứa bảng "3 tài liệu / 10 ngày" không lọt top-3.

### CP6 — A/B bắt buộc trên cả ba chiến lược

Chạy câu 1 hai lần (có và không có `metadata_filter`) trên ba chiến lược:

Với `text-embedding-3-small`, `top_k=5`:

| Chiến lược | Có filter | Không filter |
|---|---|---|
| heading | **2/2** — gold hạng 1, ngữ cảnh có "10 ngày" | **0/2** — gold vẫn hạng 1 nhưng ngữ cảnh **mất** "10 ngày" |
| recursive | **2/2** — gold hạng 1 | **0/2** — gold tụt hạng 2, ngữ cảnh mất đáp án |
| fixed_size | **2/2** — gold hạng 1 | 1/2 — gold tụt hạng 2 |

Ba kết luận:

1. **Bộ lọc có tác dụng thật trên cả ba chiến lược.** Kết quả hai lần khác nhau ở mọi chiến lược, nên câu hỏi này đúng là câu cần filter.
2. **Ca `heading` là ca đắt nhất.** Không lọc thì gold doc **vẫn ở hạng 1**, nhưng các slot còn lại bị chunk của trường khác và đối tượng khác chiếm, và chunk chứa bảng "10 ngày" bị đẩy ra ngoài. Nếu chỉ chấm bằng `doc_id` thì câu này trông như **đúng** (gold hạng 1!) trong khi agent không có gì để trả lời. Đây là bằng chứng mạnh nhất cho việc phải chấm ở mức nội dung.
3. Không lọc thì tài liệu **giảng viên** và tài liệu **trường khác** đều chen vào top-5 dù câu hỏi ngầm hỏi về sinh viên HUIT.

**Với `MockEmbedder` (đối chiếu):** heading **0/2 ngay cả khi có filter**. Tức là **filter là điều kiện cần, không phải điều kiện đủ**; embedding yếu thì lọc đúng vẫn hỏng.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, và rõ nhất ở **câu 1**. Với `gemini-embedding-001`: có lọc `{"audience":"student","institution":"huit"}` thì top-1 là chunk bảng hạn mức sinh viên HUIT (+0.8475) và câu trả lời đúng **10 ngày**. Không lọc thì gold **biến mất hoàn toàn khỏi top-3**, thay bằng `ut-muon-tra-can-bo-giang-vien#3` (+0.8615), `ut-muon-tra-sinh-vien#4` (+0.8615) và `ptit-muon-ve-nha-can-bo-giang-vien#3` (+0.8605) — sai cả trường lẫn đối tượng.
> Hai chi tiết đắt: (1) **điểm khi không lọc còn cao hơn khi có lọc** (+0.8615 so với +0.8475) — điểm cao không đồng nghĩa đúng, và đây là lý do `search_with_filter` phải lọc *trước* rồi mới search; (2) hạng 1 và hạng 2 khi không lọc có **điểm bằng nhau tuyệt đối (+0.8615)**, một bản giảng viên một bản sinh viên, vì hai file chứa đoạn văn giống hệt. Không có `audience` thì không có tín hiệu nào để chọn đúng.
> Bộ lọc có quá khắt khe không? Ở câu 1 thì tập ứng viên còn đúng 4 chunk, vẫn đủ. Nhưng nếu người dùng thật sự là giảng viên mà hệ thống mặc định lọc `audience=student` thì họ sẽ nhận sai đáp án — nên trong hệ thực, `audience` phải lấy từ **hồ sơ người đăng nhập**, không phải hard-code trong query.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Phân công demo 6–8 phút** (Kiệt dẫn):

| Phút | Nội dung | Người trình bày |
|---|---|---|
| 0–1 | Chủ đề và bộ tài liệu: vì sao chọn quy định thư viện, 9 file / 4 trường, cách tách theo `audience` | Trung (R1) |
| 1–3 | Mỗi người tóm tắt chiến lược của mình (30 giây/người) | Cả nhóm |
| 3–6 | So sánh và giải thích chiến lược nào thắng — kèm bảng hai cách chấm và A/B của bộ lọc | Kiên (R3) |
| 6–7 | Demo trực tiếp 2 câu trên `demo_ui.py`: một câu có lọc (ra đáp án đúng) và một câu ngoài phạm vi (guardrail chặn) | Thành (R2) |
| 7–8 | Hỏi đáp | Kiệt |

Terminal mở sẵn `python bench.py` đã chạy xong và `python demo_ui.py` đã lên ở `http://127.0.0.1:8000` trước khi tới lượt — demo live mà phải debug tại chỗ là mất điểm.

**Ba câu giảng viên hay hỏi, nhóm chuẩn bị sẵn:**

- *Chuyển sang chủ đề khác thì chiến lược nào còn dùng được?* `RecursiveChunker` — không phụ thuộc văn bản có heading. `HeadingChunker` chỉ ăn với văn bản có cấu trúc điều/mục; gặp FAQ hay email thì gần như vô dụng.
- *Metadata filter giúp ở đâu và làm mất kết quả ở đâu?* Giúp ở câu 1: không lọc thì cả ba chiến lược đều 0/2. Làm mất kết quả ở câu 5: lọc `audience` cứng khiến guardrail coi câu hỏi là mơ hồ và từ chối trả lời, dù hai đối tượng có cùng mức bồi thường — mất 1 điểm vì precision đổi lấy recall.
- *Nhóm học được gì từ nhóm khác?* (điền sau buổi demo)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Metadata schema chỉ có giá trị khi dữ liệu được cắt theo đúng chiều định lọc.** Trang HUIT gộp hạn mức sinh viên (10 ngày) và giảng viên (180 ngày) trong một bảng. Lưu nguyên thành một file `audience: all` thì schema nhìn rất đẹp nhưng `metadata_filter` không lọc được gì — hai đáp án nằm chung một tài liệu. Quyết định cứu câu hỏi số 1 là một quyết định về **dữ liệu**, không phải về thuật toán.
2. **Điểm similarity cao không đồng nghĩa đúng.** Câu 1 khi *không* lọc cho điểm cao hơn khi *có* lọc (+0.2897 so với +0.1538), nhưng top-3 lại toàn tài liệu sai trường và sai đối tượng. Đây là lý do `search_with_filter` phải lọc *trước* rồi mới search.
3. **Đơn vị chunk nên theo đơn vị mà người soạn văn bản đã chia.** Cùng file PTIT 2038 ký tự: fixed-size ra 5 chunk gộp 3–4 điều mỗi chunk, HeadingChunker ra 15 chunk trùng đúng 15 điều khoản. Với văn bản quy định thì chunk ngắn mà đúng ranh giới lại tốt hơn chunk dài mà cắt ngang.
4. **Nói thẳng giới hạn của phép đo.** `MockEmbedder` băm MD5 nên không có ngữ nghĩa; mọi kết luận "chiến lược nào thắng" ở cấu hình này chỉ dựa trên chất lượng ranh giới chunk đọc bằng mắt, không dựa trên score.
5. **Cách chấm quyết định kết luận.** Chấm ngây thơ (`doc_id` trong top-3) cho heading 5/5 và by_sentences 5/5; chấm theo nội dung cho 6/10 và 4/10. Hai chiến lược "đẹp nhất" theo cách chấm cũ lại là hai chiến lược tệ nhất theo cách chấm đúng. Đây là phát hiện đáng giá nhất của buổi lab.
6. **Guardrail phải chặn được cả hai kiểu hỏng, không chỉ một.** Agent hiện có bốn lớp: store rỗng, bộ lọc không còn ứng viên, điểm dưới ngưỡng (không tìm thấy thông tin liên quan → **không gọi LLM**), và câu hỏi mơ hồ về đối tượng (hỏi lại thay vì đoán). Lớp thứ tư quan trọng nhất với corpus quy định: câu "Được mượn tối đa bao nhiêu ngày?" không nêu người hỏi là ai sẽ nhận câu hỏi ngược "Bạn đang hỏi với tư cách đối tượng bạn đọc nào?" chứ không nhận một con số có 50% khả năng sai.

### CP6 — Phân tích lỗi (failure case)

Bốn ca dưới đây đều là lỗi **thật, đã đo được**, và ba trong bốn đã sửa xong; ca còn lại là đánh đổi có chủ ý.

**Ca 1 — chunk chỉ có tiêu đề chiếm slot top-k. ĐÃ SỬA.**

- *Hỏng ở đâu:* câu 2, top-1 là `huit-han-muc-muon-sinh-vien#0` — một dòng tiêu đề, **không có nội dung nào**, thắng nhờ lặp từ khoá của câu hỏi. Câu 2 chỉ được 1/2.
- *Vì sao:* `HeadingChunker` tạo một chunk cho mọi section, kể cả section chỉ có heading mà phần thân nằm ở section con. Những chunk rỗng này có tỉ lệ từ khoá trên độ dài rất cao nên cosine ưu ái chúng.
- *Sửa:* bỏ section không có thân. Corpus chuẩn **54 → 33 chunk**, độ dài trung bình 189.6 → 235.8. Câu 2 lên **2/2**, và corpus mở rộng hết tụt điểm (trước 9→7, sau 9→8).

**Ca 2 — `top_k=3` quá chật với chunk ngắn. ĐÃ SỬA.**

- *Hỏng ở đâu:* câu 5, chunk chứa `gấp 03 lần` (mục "Xử lý vi phạm" của file sinh viên) xếp **hạng 4** nên không lọt top-3. Ngữ cảnh mất đáp án → 0/2.
- *Vì sao:* cosine đo **độ giống chủ đề**, không đo **mật độ thông tin trả lời được**. Mục "Quy định chung" của cả hai file (nói về xuất trình thẻ) giành hạng 1 và 2 vì cùng chủ đề "mượn trả tài liệu", đẩy mục có đáp án ra ngoài.
- *Sửa:* `top_k` mặc định 3 → **5**. Câu 5 lên 1/2, `heading` từ 8/10 lên 10/10 (retrieval). Chunk trung bình 235 ký tự thì 3 slot chỉ gom được ~700 ký tự ngữ cảnh — quá ít cho một văn bản quy định.

**Ca 3 — hàm chấm cho điểm sai. ĐÃ SỬA.**

- *Hỏng ở đâu:* ở bản chạy trước, câu 5 được **2/2** trong khi chunk hạng 1 của tài liệu gold là mục "Quy định chung" **không chứa** mức bồi thường; chuỗi `gấp 03 lần` đến từ file **giảng viên** ở hạng 3.
- *Vì sao:* hàm chấm kiểm "gold doc ở hạng 1" và "chuỗi có trong ngữ cảnh" **độc lập nhau**, nên hai điều kiện được thoả bởi **hai tài liệu khác nhau** vẫn ra điểm tối đa.
- *Sửa:* thêm **mức 2b** (chuỗi phải nằm trong chunk thuộc gold doc) và **mức 3** (`docs/SCORING.md` đòi agent phải trả lời được). Đây là tầng sâu hơn của chính bài học "cách chấm quyết định kết luận".

**Ca 4 — guardrail `ambiguous` quá thận trọng. CHƯA SỬA, là đánh đổi có chủ ý.**

- *Hỏng ở đâu:* câu 5 hiện được 1/2 chứ không phải 2/2. Retrieval đúng hoàn toàn (gold hạng 1, ngữ cảnh có đáp án) nhưng agent **từ chối trả lời**: top-k trải trên `student` và `faculty`, hạng 1 và hạng 2 chênh 0.0083 < `RAG_MARGIN=0.02`.
- *Vì sao:* việc tách file theo `audience` ở CP2 đã **nhân đôi phần nội dung dùng chung** — mục "Quy định chung" và "Xử lý vi phạm" của UTH gần như giống hệt nhau giữa hai file. Guardrail thấy hai đối tượng khác nhau nên cho rằng đáp án có thể khác nhau, trong khi thực tế **mức bồi thường của hai nhóm là một**.
- *Đánh đổi:* nới `RAG_MARGIN` hoặc bỏ lớp này sẽ lấy lại 1 điểm, nhưng đúng lớp đó mới chặn được câu "Được mượn tối đa bao nhiêu ngày?" — nơi hai đối tượng **thật sự** có đáp án khác nhau (10 ngày so với 180 ngày). Chúng tôi chọn giữ, vì trong hệ tra cứu quy định thì trả lời sai đối tượng tai hại hơn là hỏi lại một câu thừa. Cách sửa đúng nằm ở **dữ liệu**, không ở ngưỡng: gom phần dùng chung của UTH về một file `audience: all`, chỉ để lại con số riêng trong hai file tách.

**Bài học rút ra khi so sánh trong nhóm:**
> Bốn người, bốn chiến lược, cùng một corpus và cùng một lượt chạy. Điều bất ngờ nhất là **khoảng cách giữa bốn chiến lược nhỏ hơn nhiều so với nhóm dự đoán**: với embedding thật, ba trong bốn đạt 10/10 và cả bốn đều 5/5 doc-hit. Khác biệt chỉ lộ ra khi đổi *cấu hình khác*: với `MockEmbedder`, cùng bốn chiến lược đó giãn ra 4/10 đến 7/10.
> Nói cách khác, chiến lược chunking **không phải** biến số quan trọng nhất ở quy mô này. Ba biến số mạnh hơn, đo được: embedding (6→9 điểm), `top_k` (8→10 điểm), và bộ lọc metadata (2/2 → 0/2 khi bỏ lọc). Bài học nhóm rút ra là phải sửa theo thứ tự **dữ liệu → metadata → top_k → embedding → chunking**, chứ không bắt đầu từ chunking như trực giác ban đầu.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Ba thứ. (1) Chạy benchmark bằng embedding thật (`EMBEDDING_PROVIDER=local` với `paraphrase-multilingual-MiniLM`) ngay từ đầu thay vì để mock tới cuối — hiện tại 5/5 HIT@3 là nhờ metadata thu hẹp tập ứng viên chứ không nhờ retrieval. (2) Thêm `audience: staff` và tài liệu ký túc xá/học phí để `audience` có đủ 4 giá trị và bộ lọc bị thử thách thật sự. (3) Chuẩn hoá `document_version` về một dạng duy nhất — hiện có ba dạng (`not-stated`, số hiệu quyết định, ngày cập nhật), khó dùng để lọc phiên bản mới/cũ.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **38 / 40** |

> Chất lượng truy xuất **9/10** theo đúng thang ba mức của `docs/SCORING.md`, chạy với `text-embedding-3-small` + `gpt-4o-mini`, `top_k=5`. Bốn câu đạt 2/2; câu 5 được 1/2 vì guardrail `ambiguous` chặn agent dù retrieval đúng — đánh đổi có chủ ý, xem phân tích lỗi ca 4.
