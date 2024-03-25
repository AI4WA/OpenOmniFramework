# Use an official Node.js runtime as a parent image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in package.json
RUN npm install
RUN npm install next -g
# Build the Next.js application
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define the command to run your app using CMD which defines your runtime
# Start the development server
CMD ["npm", "run", "dev"]