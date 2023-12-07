def upsert_batchs(self, ids, payloads, vectors):
    batch_size = 25
    ids = self.batched(ids, batch_size)
    payloads = self.batched(payloads, batch_size)
    vectors = self.batched(vectors, batch_size)
    batch_num = len(ids)
    for i in range(batch_num):
        print("Upserting batch", i+1)
        print("sdsd")
        print("Upserted batch", i+1)
