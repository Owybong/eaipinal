module.exports = {
  development: {
    url: process.env.DATABASE_URL || 'postgres://user:password@localhost:5432/inventory_db',
    dialect: 'postgres',
  },
  test: {
    dialect: 'sqlite',
    storage: './database_test.sqlite',
    logging: false
  },
  production: {
    url: process.env.DATABASE_URL,
    dialect: 'postgres'
  }
} 