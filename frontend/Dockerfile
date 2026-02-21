# Use Nginx Alpine for lightweight container
FROM nginx:alpine

# Copy all frontend files to Nginx web root
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY novnc-control.js /usr/share/nginx/html/

# Copy custom Nginx configuration (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Nginx will start automatically with the base image's CMD