# 🏁 GR Cup Dashboard Version Management Guide

## Overview
This versioning system helps track and manage different versions of the dashboard, making it easy to rollback to working versions when needed.

## Quick Commands

### Create a New Version
```bash
python dashboard/version_manager.py create v1.1 "Description of changes"
```

### List All Versions
```bash
python dashboard/version_manager.py list
```

### Rollback to Previous Version
```bash
python dashboard/version_manager.py rollback v1.0
```

### Deploy Current Version to S3
```bash
python dashboard/version_manager.py deploy
```

## Version Naming Convention

- **v1.0** - Major stable releases
- **v1.1** - Minor feature additions
- **v1.1.1** - Bug fixes and patches
- **v2.0** - Major overhauls or breaking changes

## Version Status

- ✅ **Working** - Tested and functional
- ❌ **Broken** - Known issues or non-functional

## Current Version Status

### v1.0 - ✅ STABLE BASELINE
- **Features**: Real track images, simulated telemetry, track selector
- **Status**: Fully functional
- **Description**: Working baseline with real track images and simulated telemetry
- **Live URL**: https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html

## File Structure

```
dashboard/
├── track_dashboard.html          # Current active version
├── track_images_embedded.js      # Track image data
├── version_manager.py            # Version management script
├── VERSION_GUIDE.md             # This guide
└── versions/                    # Version archive
    ├── version_log.json         # Version history
    ├── track_dashboard_v1.0_working_*.html
    └── track_dashboard_v*.html
```

## Best Practices

1. **Always create a version before making changes**:
   ```bash
   python dashboard/version_manager.py create v1.1 "Adding new feature X"
   ```

2. **Test thoroughly before marking as working**

3. **Use descriptive version descriptions**

4. **Keep working versions for easy rollback**

5. **Deploy only tested versions**:
   ```bash
   python dashboard/version_manager.py deploy
   ```

## Emergency Rollback

If the dashboard breaks:

1. **List available versions**:
   ```bash
   python dashboard/version_manager.py list
   ```

2. **Rollback to last working version**:
   ```bash
   python dashboard/version_manager.py rollback v1.0
   ```

3. **Deploy the rollback**:
   ```bash
   python dashboard/version_manager.py deploy
   ```

## Version History

- **v1.0** (2025-11-05) - Initial stable version with real track images ✅

---

*This versioning system ensures we can always return to a working state quickly and track our development progress effectively.*