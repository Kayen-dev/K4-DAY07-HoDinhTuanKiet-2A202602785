# Ke hoach K4-L3A

## Branch

Branch dang lam: `feature/l3a-university-services`

## Chu de nen chon

Da chon: dich vu va quy dinh Thu vien UIT.

Ly do phu hop:
- Thuoc dung rang buoc L3A: dich vu/quy dinh dai hoc.
- Co nguon cong khai, chinh thuc tu website Thu vien UIT.
- Co nhieu metadata co ich: `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version`.
- De tao cau hoi can metadata filter, vi thong tin tai khoan/CSDL cua sinh vien va giang vien khac nhau.
- Cac trang co cau truc theo muc, phu hop cho chien luoc chunk theo heading.

## Cac chu de khac cung phu hop

1. Dang ky hoc phan: phu hop neu co trang hoc vu cong khai ve lich dang ky, dieu kien tien quyet, huy/dieu chinh lop. Kho hon o cho nhieu truong de trong cong sinh vien can dang nhap.
2. Hoc phi: phu hop vi co con so, moc thoi gian, doi tuong sinh vien; can tranh trang PDF/scan kho crawl.
3. Hoc bong: phu hop vi co dieu kien, ho so, han nop; metadata `audience=student`, `category=scholarship` rat ro.
4. Ky tuc xa: phu hop neu co noi quy, phi, thoi gian dang ky, doi tuong; de tao query can loc `student`.
5. Phuc khao: phu hop vi quy trinh ngan, co thoi han va le phi; thuong it tai lieu nen co the kho dat 5-10 file.

Xep hang khuyen nghi:
1. Thu vien UIT
2. Hoc bong
3. Phuc khao
4. Hoc phi
5. Dang ky hoc phan
6. Ky tuc xa

## Du lieu da tao

Thu muc corpus: `data/library-uit`

So tai lieu: 6 file Markdown.

Phan bo audience:
- `student`: 2
- `faculty`: 1
- `all`: 3

File benchmark chung: `data/library-uit/benchmark_queries.csv`

## Chia vai nhom

R1 Data:
- Giu `data/library-uit/sources.csv`.
- Kiem tra moi file co du metadata bat buoc.
- Dam bao source URL la nguon cong khai va noi dung da duoc lam sach.

R2 Benchmark:
- Dung 5 cau hoi trong `data/library-uit/benchmark_queries.csv`.
- Kiem tra tung gold answer co the doi chieu lai trong file Markdown va URL goc.

R3 Strategy:
- Dam bao moi thanh vien dung chien luoc chunking khac nhau.
- Nhan phan chunk theo heading vi day la rang buoc bat buoc cua lop.

## Chien luoc chunking khuyen nghi

Thanh vien 1: `FixedSizeChunker(chunk_size=350, overlap=50)`
- Tot de lam baseline don gian.
- Co overlap giup giu ngu canh khi cau tra loi nam gan bien chunk.

Thanh vien 2: `RecursiveChunker(chunk_size=450)`
- Phu hop voi van ban co doan ngan va danh sach.
- Thu tach theo dong trong, dong moi, cau, khoang trang.

Thanh vien 3: custom heading chunker
- Tach theo cac heading Markdown `#`, `##`, `###`.
- Phu hop nhat voi corpus nay vi cac file da co muc nhu "Ten dang nhap", "Co so du lieu dung chung", "Luu y".

## Cau hoi bat buoc can metadata filter

Cau nen dung: "Sinh vien tu nam 2 tro di muon gia han quyen truy cap co so du lieu dung chung thi phi moi nam la bao nhieu?"

Filter can dung: `metadata_filter={"audience": "student"}`

Ly do: cung la trang tai khoan Thu vien, nhung sinh vien tu nam 2 phai gia han 25.000 dong/nam, trong khi can bo - giang vien duoc mien phi. Neu khong loc `audience`, retrieval de lay nham file `library-account-faculty`.
