# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hồ Đình Tuấn Kiệt
**Nhóm:** K4-L3A
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector văn bản gần cùng hướng, tức hai đoạn có nội dung/ngữ nghĩa gần nhau theo cách embedding biểu diễn. Với retrieval, điểm cao thường là dấu hiệu chunk có khả năng liên quan đến câu hỏi.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên được mượn 5 cuốn giáo trình trong 90 ngày.
- Câu B: Chính sách cho phép sinh viên mượn tối đa 5 giáo trình trong thời hạn 90 ngày.
- Tại sao tương đồng: Hai câu cùng nói về đối tượng sinh viên, số lượng giáo trình và thời hạn mượn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên gia hạn CSDL với phí 25.000 đồng mỗi năm.
- Câu B: Thư viện mở cửa thứ Bảy từ 08:00 đến 16:00.
- Tại sao khác: Hai câu thuộc hai nghiệp vụ khác nhau: tài khoản/CSDL và thời gian phục vụ.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, nên phù hợp để so sánh ý nghĩa hơn là độ lớn tuyệt đối. Với embeddings đã chuẩn hóa, dot product bằng cosine similarity nên tính nhanh và ổn định.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23.
> Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, step còn 400 nên số chunk là ceil((10000 - 100) / 400) = 25. Overlap cao hơn làm tăng số chunk nhưng giúp giữ ngữ cảnh ở ranh giới giữa hai chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex tách tại vị trí sau dấu câu: `(?<=[.!?])\s+|(?<=\.)\n+`, nhờ vậy dấu `.`, `!`, `?` không bị nuốt mất. Sau khi tách, tôi gom tối đa `max_sentences_per_chunk` câu thành một chunk và strip khoảng trắng thừa. Edge case chưa xử lý hoàn hảo là chữ viết tắt như `TS.`, `v.v.` hoặc số thập phân có thể bị cắt sai.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi thử các separator theo thứ tự từ lớn đến nhỏ: dòng trống, dòng mới, câu, khoảng trắng, rồi fallback cắt cứng. Nếu một mảnh vẫn dài hơn `chunk_size`, `_split` gọi đệ quy với danh sách separator còn lại; nếu các mảnh nhỏ liền kề có thể ghép lại mà không vượt `chunk_size`, tôi gom chúng để tránh chunk vụn. Base case là text đã đủ ngắn, hết separator, hoặc separator rỗng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` không tự chunk; mỗi `Document` đầu vào được embed và lưu thành một record. `search` embed query, tính cosine similarity giữa query vector và từng record, sau đó sort giảm dần theo `score` và lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước rồi mới tính similarity trên tập còn lại, vì như vậy query như `audience=student` không bị nhiễu bởi tài liệu của giảng viên. `delete_document` xóa mọi record có `metadata["doc_id"]` hoặc `doc_id` trùng với id cần xóa, và trả về `True` nếu kích thước store giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search(question, top_k)` để lấy các chunk liên quan, sau đó dựng prompt gồm phần hướng dẫn, danh sách context đánh số kèm source, câu hỏi và nhãn `Answer:`. Prompt yêu cầu chỉ trả lời dựa trên context; nếu context thiếu thì nói không có trong knowledge base.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 42 items
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên mượn giáo trình 90 ngày | Sinh viên được mượn 5 giáo trình | cao | 0.82 | Đúng |
| 2 | Gia hạn CSDL 25.000 đồng/năm | Phí truy cập cơ sở dữ liệu cho sinh viên | cao | 0.71 | Đúng |
| 3 | Thư viện mở cửa thứ Bảy | Lịch phục vụ cuối tuần | cao | 0.67 | Đúng |
| 4 | Gia hạn sách trước ngày hết hạn | Mật khẩu mặc định là 1-8 | thấp | 0.12 | Đúng |
| 5 | Cán bộ giảng viên miễn phí CSDL | Sinh viên năm 2 đóng phí CSDL | trung bình | 0.43 | Đúng một phần |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 dễ gây nhầm vì cùng nói về CSDL nhưng đáp án khác theo `audience`. Điều này cho thấy chỉ similarity nội dung chưa đủ; metadata filter rất quan trọng để phân biệt đối tượng áp dụng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên UIT được mượn giáo trình tại Thư viện UIT bao nhiêu cuốn trong bao lâu và được gia hạn mấy lần? | `library-borrowing-student` chunk 3: chính sách tại Thu viện UIT, giao trình 5 cuốn/90 ngày/gia hạn 2 lần. | 0.720 | Có | Sinh viên được mượn 5 cuốn giáo trình trong 90 ngày, gia hạn 2 lần, mỗi lần 15 ngày. |
| 2 | Sinh viên từ năm 2 trở đi muốn gia hạn quyền truy cập CSDL dùng chung thì phí mỗi năm là bao nhiêu? | `library-account-student` chunk 4: cơ sở dữ liệu dùng chung, sinh viên năm 2 trở đi gia hạn 25.000 đồng/năm. | 0.685 | Có | Sinh viên từ năm 2 trở đi cần gia hạn quyền truy cập với phí 25.000 đồng/năm tại TVTT. |
| 3 | Cán bộ giảng viên UIT truy cập CSDL dùng chung có mất phí không? | `library-account-faculty` chunk 4: cán bộ - giảng viên được miễn phí quyền truy cập CSDL dùng chung. | 0.639 | Có | Cán bộ - giảng viên được miễn phí quyền truy cập CSDL dùng chung. |
| 4 | Thư viện UIT mở cửa thứ Bảy lúc mấy giờ và đóng cửa lúc mấy giờ? | `library-hours` chunk 2: thứ Bảy mở cửa 08:00 và đóng cửa 16:00. | 0.667 | Có | Thứ Bảy thư viện mở cửa lúc 08:00 và đóng cửa lúc 16:00. |
| 5 | Bạn đọc cần làm gì để gia hạn tài liệu và chỉ được gia hạn trước ngày hết hạn bao lâu? | `library-renewal-guide` chunk 3: chỉ được gia hạn trước ngày hết hạn 1 hoặc 2 ngày. | 0.593 | Có | Đăng nhập, chọn tài liệu, chọn Renew Marked, xác nhận Yes; chỉ gia hạn trước hạn 1 hoặc 2 ngày. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng metadata schema phải khớp với câu hỏi benchmark, nếu không filter chỉ là hình thức. Việc tách file sinh viên và giảng viên giúp query CSDL trả lời đúng hơn nhiều so với để chung `audience=all`.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |
