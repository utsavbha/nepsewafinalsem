# NepSewa Render Deployment Guide

## Prerequisites
1. GitHub account with your NepSewa code pushed
2. Render account (free tier available)

## Step 1: Prepare Your Repository

Make sure your repository has these files:
- `requirements.txt` - Python dependencies
- `render_start.py` - Production startup script
- `Procfile` - Process configuration
- `render.yaml` - Render configuration (optional)

## Step 2: Create Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL" or "MySQL"
3. Choose "MySQL" for NepSewa
4. Configure:
   - **Name**: `nepsewa-db`
   - **Database**: `nepsewa`
   - **User**: `nepsewa_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is sufficient for testing
5. Click "Create Database"
6. **Important**: Copy the "Internal Database URL" - you'll need this

## Step 3: Deploy Web Service

1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `nepsewa-app`
   - **Environment**: `Python 3`
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_start.py`

## Step 4: Configure Environment Variables

In your web service settings, add these environment variables:

### Required Variables:
- `DATABASE_URL`: Use the Internal Database URL from Step 2
- `PORT`: `10000` (Render sets this automatically)

### Optional Variables (for enhanced security):
- `FLASK_SECRET_KEY`: Generate a random secret key
- `ESEWA_MERCHANT_CODE`: Your eSewa merchant code
- `ESEWA_SECRET_KEY`: Your eSewa secret key

## Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your application with `render_start.py`

## Step 6: Verify Deployment

1. Once deployed, visit your Render URL (e.g., `https://nepsewa-app.onrender.com`)
2. Check these endpoints:
   - `/health` - Should return database status
   - `/services` - Should load the services page
   - `/` - Should load the home page

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Verify `DATABASE_URL` is correctly set
   - Ensure database and web service are in the same region
   - Check database is running and accessible

2. **Application Won't Start**
   - Check build logs for dependency issues
   - Verify `render_start.py` is in the repository root
   - Ensure all required files are committed to Git

3. **Static Files Not Loading**
   - Verify `static/` folder is in your repository
   - Check file paths in templates are correct

### Viewing Logs:
- Go to your web service in Render Dashboard
- Click "Logs" tab to see real-time application logs
- Check both "Build" and "Deploy" logs for issues

## Production Considerations

### Database:
- Free tier MySQL has limitations (1GB storage, 1 month retention)
- Consider upgrading to paid plan for production use
- Regular backups are recommended

### Performance:
- Free tier web service sleeps after 15 minutes of inactivity
- First request after sleep may be slow (cold start)
- Consider paid plan for always-on service

### Security:
- Change default admin password (`admin123`)
- Use environment variables for sensitive data
- Enable HTTPS (Render provides this automatically)

### Monitoring:
- Set up health check monitoring
- Monitor database usage and performance
- Set up alerts for service downtime

## Custom Domain (Optional)

1. In your web service settings, go to "Settings" → "Custom Domains"
2. Add your domain name
3. Configure DNS records as instructed by Render
4. SSL certificate will be automatically provisioned

## Scaling

For high traffic:
1. Upgrade to paid Render plan
2. Consider database optimization
3. Implement caching (Redis)
4. Use CDN for static assets

## Support

- Render Documentation: https://render.com/docs
- NepSewa Issues: Check your repository issues
- Database Issues: Check Render database logs

---

**Your NepSewa application should now be live on Render! 🚀**

Visit your deployment URL and test all functionality including:
- User registration/login
- Service booking
- Provider management
- Payment processing
- Admin dashboard