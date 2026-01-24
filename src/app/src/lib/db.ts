export interface DBRecord {
  id: string
  createdAt: number
  updatedAt: number
  [key: string]: any
}

class LocalDatabase<T extends DBRecord> {
  private storageKey: string
  private data: Map<string, T> = new Map()

  constructor(collection: string) {
    this.storageKey = `codeai_db_${collection}`
    this.load()
  }

  private load(): void {
    if (typeof window === 'undefined') return
    const stored = localStorage.getItem(this.storageKey)
    if (stored) {
      const records: T[] = JSON.parse(stored)
      records.forEach(r => this.data.set(r.id, r))
    }
  }

  private save(): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(this.storageKey, JSON.stringify(Array.from(this.data.values())))
  }

  create(record: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): T {
    const now = Date.now()
    const newRecord = {
      ...record,
      id: `${this.storageKey}_${now}`,
      createdAt: now,
      updatedAt: now,
    } as T
    this.data.set(newRecord.id, newRecord)
    this.save()
    return newRecord
  }

  read(id: string): T | null {
    return this.data.get(id) ?? null
  }

  readAll(): T[] {
    return Array.from(this.data.values())
  }

  update(id: string, updates: Partial<T>): T | null {
    const record = this.data.get(id)
    if (!record) return null
    const updated = { ...record, ...updates, updatedAt: Date.now() }
    this.data.set(id, updated)
    this.save()
    return updated
  }

  delete(id: string): boolean {
    const deleted = this.data.delete(id)
    if (deleted) this.save()
    return deleted
  }
}

export function createDatabase<T extends DBRecord>(collection: string) {
  return new LocalDatabase<T>(collection)
}
