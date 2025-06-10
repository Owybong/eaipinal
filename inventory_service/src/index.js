const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const cors = require('cors');
const typeDefs = require('./graphql/schema');
const resolvers = require('./graphql/resolvers');
const sequelize = require('./database');
const { Warehouse, Inventory } = require('./models');
const restAdapter = require('./restAdapter');

// Create an Express application
const app = express();

// Apply middleware
app.use(cors());
app.use(express.json());

// Add a route handler for the root path
app.get('/', (req, res) => {
  res.send('Welcome to Inventory Services API. Please use the GraphQL endpoint at /graphql or REST endpoints');
});

// Mount the REST adapter routes
app.use('/', restAdapter);

// Create an Apollo server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  cache: "bounded",
  context: ({ req }) => {
    // Here you can add authentication logic if needed
    return {
      models: {
        Warehouse,
        Inventory
      }
    };
  },
  playground: true, // Enable GraphQL playground
  introspection: true // Enable introspection in production
});

// Start the server
async function startServer() {
  try {
    // Test the database connection
    await sequelize.authenticate();
    console.log('Database connection has been established successfully.');
    
    await sequelize.sync(); // This will create tables if they don't exist
    
    // Start the Apollo server
    await server.start();
    
    // Apply middleware to Express
    server.applyMiddleware({ app });
    
    // Define a port
    const PORT = process.env.PORT || 5003;
    
    // Start the Express server
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`Server is running at http://0.0.0.0:${PORT}`);
      console.log(`GraphQL endpoint is at http://0.0.0.0:${PORT}${server.graphqlPath}`);
      console.log(`REST endpoints are available at http://0.0.0.0:${PORT}/`);
    });
  } catch (error) {
    console.error('Error starting server:', error);
  }
}

startServer(); 