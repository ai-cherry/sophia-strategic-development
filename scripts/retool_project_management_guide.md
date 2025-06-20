# Sophia Project Management - Retool Implementation Guide

## 🚀 Overview
This Retool application provides a unified project intelligence dashboard that aggregates data from Linear, GitHub, Asana, and Slack to provide comprehensive project insights aligned with company OKRs.

## 📋 Prerequisites
1. Sophia AI backend running with project management routes enabled
2. Linear API key configured
3. GitHub integration connected
4. Slack bot configured
5. Retool account with API resource capabilities

## 🛠️ Setup Instructions

### 1. Create New Retool App
1. Log into Retool
2. Create a new app named "Sophia Project Intelligence"
3. Set the theme to match your brand

### 2. Configure API Resource
1. Go to Resources → Add Resource → REST API
2. Configure as follows:
   - Name: `ProjectManagementAPI`
   - Base URL: `https://your-sophia-backend.com/api/project-management`
   - Headers:
     - Authorization: `Bearer {{ environment.SOPHIA_API_KEY }}`
     - Content-Type: `application/json`

### 3. Import Configuration
1. Open the app editor
2. Go to Settings → App JSON
3. Copy the contents of `retool_project_management_config.json`
4. Paste and save

### 4. Environment Variables
Set these in Retool's environment settings:
- `SOPHIA_API_URL`: Your Sophia backend URL
- `SOPHIA_API_KEY`: Your API authentication key

## 🎯 Key Features

### Portfolio Overview
- Real-time project status across all tools
- Progress tracking with visual indicators
- Multi-source integration badges
- Detailed project drill-down

### OKR Alignment
- Quarterly OKR tracking
- Project contribution mapping
- Progress visualization
- Risk identification

### Blocker Analysis
- Cross-project blocker detection
- Pattern recognition
- AI-generated resolutions
- Priority-based recommendations

### Team Performance
- Team health scores
- Velocity tracking
- Sentiment analysis from Slack
- Resource allocation insights

### Analytics & Reporting
- Trend analysis over time
- Custom report builder
- Export capabilities
- Predictive insights

## 🔧 Customization

### Adding New Metrics
1. Update the backend agent to calculate new metrics
2. Add to the `selectedMetrics` options in custom report builder
3. Update the project table columns if needed

### Modifying OKRs
1. Update the OKR structure in `ProjectIntelligenceAgent`
2. The UI will automatically reflect new objectives and key results

### Custom Integrations
1. Add new data sources to the backend agent
2. Update the source badges in the project table
3. Add new tabs or sections as needed

## 📊 Usage Tips

### For Executives
- Start with the Portfolio Overview for high-level status
- Check OKR Alignment weekly to track progress
- Review Recommendations for strategic actions

### For Project Managers
- Use Blockers & Actions tab daily
- Monitor Team Performance for resource needs
- Create custom reports for stakeholder updates

### For Team Leads
- Track team velocity trends
- Address blockers quickly
- Use sentiment data to gauge team morale

## 🚨 Troubleshooting

### No Data Loading
1. Check API connection in browser console
2. Verify authentication token
3. Ensure backend is running

### Slow Performance
1. Reduce polling intervals
2. Implement pagination for large datasets
3. Use caching where appropriate

### Missing Projects
1. Verify all integrations are connected
2. Check project name matching logic
3. Review unification algorithm

## 📈 Best Practices

1. **Regular Updates**: Keep OKRs current with weekly updates
2. **Action Items**: Address critical recommendations within 24 hours
3. **Team Sync**: Use team performance data in 1-on-1s
4. **Custom Reports**: Save frequently used report configurations

## 🔗 Related Documentation
- [Project Intelligence Agent Documentation](../backend/agents/specialized/project_intelligence_agent.py)
- [API Route Documentation](../backend/app/routes/project_management_routes.py)
- [Sophia AI Architecture Guide](../docs/SOPHIA_ARCHITECTURE.md)

## 💡 Future Enhancements
- Asana integration when API key available
- GitHub project boards visualization
- Automated report scheduling
- Mobile-responsive design
- Real-time collaboration features
