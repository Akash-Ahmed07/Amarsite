# Render Deployment Guide for Amarsite.Online

This guide will help you deploy your Streamlit study platform to Render.

## Prerequisites

1. A GitHub account with this code pushed to a repository
2. A Render account (free tier available at https://render.com)

## Deployment Steps

### 1. Prepare Your Repository

Make sure these files are in your repository:
- `app.py` - Main application file
- `render_requirements.txt` - Python dependencies (rename to `requirements.txt` before deployment)
- `.streamlit/config.toml` - Streamlit configuration
- `init_db.sql` - Database schema

### 2. Create PostgreSQL Database on Render

1. Log in to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `amarsite-db` (or your preferred name)
   - **Database**: `amarsite`
   - **User**: `amarsite_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is sufficient to start
4. Click "Create Database"
5. **Important**: Copy the "External Database URL" - you'll need this

### 3. Initialize the Database

1. In Render Dashboard, go to your PostgreSQL database
2. Click "Connect" → "External Connection"
3. Use the provided connection string with a PostgreSQL client (like pgAdmin or psql)
4. Run the `init_db.sql` script to create tables:
   ```bash
   psql <YOUR_EXTERNAL_DATABASE_URL> < init_db.sql
   ```

### 4. Deploy the Web Service

1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the web service:

   **Basic Settings:**
   - **Name**: `amarsite-online` (or your preferred name)
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: 
     ```
     pip install -r render_requirements.txt
     ```
     (Note: Rename `render_requirements.txt` to `requirements.txt` in your repo)
   
   - **Start Command**: 
     ```
     streamlit run app.py --server.port $PORT --server.address 0.0.0.0
     ```

   **Environment Variables:**
   Click "Advanced" and add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the External Database URL from step 2

4. Click "Create Web Service"

### 5. Wait for Deployment

- First deployment takes 2-5 minutes
- Monitor build logs in the Render Dashboard
- Once complete, your app will be live at: `https://your-service-name.onrender.com`

## Important Notes

### Free Tier Limitations
- Apps sleep after 15 minutes of inactivity
- 30-second wake-up time when accessed after sleep
- 750 hours/month of runtime

### Auto-Deploy
- Any push to your main branch will trigger automatic redeployment
- Monitor deployments in the Render Dashboard

### Database Connection
- The app automatically uses the `DATABASE_URL` environment variable
- SSL mode is handled automatically by Render's PostgreSQL

### Troubleshooting

**Build Fails:**
- Check that `requirements.txt` has correct package names and versions
- Ensure Python 3.11+ compatibility

**App Won't Start:**
- Verify start command matches your main file name (`app.py`)
- Check logs in Render Dashboard for specific errors

**Database Connection Errors:**
- Verify `DATABASE_URL` environment variable is set correctly
- Ensure database is in the same region as web service for best performance
- Check that `init_db.sql` ran successfully

**Import Errors:**
- Ensure all dependencies are listed in `requirements.txt`
- Check that file paths are correct (case-sensitive on Linux)

## Post-Deployment

After successful deployment:

1. Test user registration and login
2. Create a study set and verify it saves to the database
3. Test all features (study mode, practice test, spaced review)
4. Set up a custom domain (optional, paid plans only)

## Updating Your App

To update your deployed app:
1. Make changes to your code locally
2. Commit and push to your GitHub repository
3. Render will automatically detect the push and redeploy

## Cost Optimization

For production use, consider:
- Upgrading to paid tier to avoid sleep mode
- Using a larger database instance for better performance
- Setting up monitoring and alerts

## Support

For issues with:
- **Render Platform**: https://render.com/docs
- **Streamlit**: https://docs.streamlit.io
- **PostgreSQL**: https://www.postgresql.org/docs/

---

Your Amarsite.Online study platform is now live and ready to use!
