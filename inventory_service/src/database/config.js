module.exports = {
  development: {
    dialect: 'sqlite',
    storage: './database.sqlite',
    logging: false
  },
  test: {
    dialect: 'sqlite',
    storage: './database_test.sqlite',
    logging: false
  },
  production: {
    dialect: 'sqlite',
    storage: './database_prod.sqlite',
    logging: false
  }
} 