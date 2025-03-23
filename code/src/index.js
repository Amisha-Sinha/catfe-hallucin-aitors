import { MongoClient } from "mongodb";

let conn = "mongodb+srv://test:123@smart-stubs.psvr9.mongodb.net/?retryWrites=true&w=majority&appName=smart-stubs";
const client = new MongoClient(conn);

async function startServer() {
  try {
    await client.connect();
    await client.db("admin").command({ ping: 1 });
    console.log("Pinged your deployment. You successfully connected to MongoDB!");

    // ... rest of the server setup
  } catch (error) {
    console.error("Error connecting to MongoDB:", error);
    process.exit(1);
  }
}

startServer();