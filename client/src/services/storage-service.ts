// Simple persistent storage service for generations using localStorage
// Usage: StorageService.getGenerations(), StorageService.addGeneration(generation)

export interface Generation {
  id: string
  name: string
  url: string
  createdAt: string
}

const STORAGE_KEY = 'generations'

export const StorageService = {
  getGenerations(): Generation[] {
    if (typeof window === 'undefined') return []
    try {
      const data = localStorage.getItem(STORAGE_KEY)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  },
  addGeneration(generation: Generation) {
    const generations = this.getGenerations()
    generations.unshift(generation)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(generations))
  },
  removeGeneration(id: string) {
    const generations = this.getGenerations().filter((g) => g.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(generations))
  },
  clear() {
    localStorage.removeItem(STORAGE_KEY)
  }
}
