class DB {
    constructor(dbName, dbVersion, stores) {
        this.dbName = dbName;
        this.dbVersion = dbVersion;
        // stores は { storeName: keyPath } の形式のオブジェクトを想定
        this.stores = stores; 
        this.db = null;
    }

    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                // 定義されているすべてのストアを確認・作成
                for (const [storeName, keyPath] of Object.entries(this.stores)) {
                    if (!db.objectStoreNames.contains(storeName)) {
                        db.createObjectStore(storeName, { keyPath });
                        console.debug(`Store created: ${storeName}`);
                    }
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onerror = () => reject(new Error("Database failed to open"));
        });
    }

    // テーブル名を指定して保存
    async save(storeName, data) {
        await this.open();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], "readwrite");
            const store = transaction.objectStore(storeName);

            const request = store.put(data);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(new Error(`Failed to save to ${storeName}`));
        });
    }

    // テーブル名を指定して取得
    async get(storeName, key) {
        await this.open();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], "readonly");
            const store = transaction.objectStore(storeName);
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(new Error(`Failed to get from ${storeName}`));
        });
    }

    async getAll(storeName) {
        await this.open()
        return new Promise((resolve,reject) => {
            const transaction = this.db.transaction([storeName],"readonly")
            const store = transaction.objectStore(storeName)
            const request = store.getAll()
            request.onsuccess = () => resolve(request.result)
            request.onerror = (e) => reject(console.error(`DBの取得エラー:${e}`))
            
        })
    }
}
