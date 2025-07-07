# Large File Audit and Cleanup

## Files to Remove

### 1. Large JSON Reports (17.2 MB total)
- `codacy_analysis_report.json` - 1.2 MB (code analysis report)
- `codacy_detailed_results.json` - 16 MB (detailed code analysis)

### 2. Large Text File
- `large_files_list.txt` - 9.3 MB (list of large files)

### 3. Package Lock Files (Should be gitignored)
- `frontend/package-lock.json`
- `infrastructure/package-lock.json`
- `infrastructure/dns/package-lock.json`
- `infrastructure/vercel/package-lock.json`
- `npm-mcp-servers/package-lock.json`

### 4. Crash Dumps (Binary files)
- `frontend/.config/chromium/Crash Reports/pending/*.dmp` (12 files)
- `frontend/.config/chromium/Crash Reports/pending/*.meta` (12 files)
- `frontend/.config/chromium/Crash Reports/settings.dat`

### 5. Other Large Reports
- `security_audit_python.json`
- `snowflake_standardization_report.json`
- `syntax_scan_results.json`
- `duplication_report.json`
- `large_file_analysis_data.json`
- `LARGE_FILE_ANALYSIS_REPORT.md`

### 6. Config Files (Should be user-specific)
- `frontend/.config/code-server/config.yaml`
- `frontend/.config/matplotlib/matplotlibrc`

## Recommendations

1. **Add to .gitignore:**
   ```
   # Large reports
   *_report.json
   *_results.json

   # Package lock files (use package manager specific)
   package-lock.json
   pnpm-lock.yaml

   # User-specific configs
   .config/

   # Crash dumps
   *.dmp
   *.meta

   # Large analysis files
   large_files_list.txt
   ```

2. **Keep these files locally** but don't commit them to Git
3. **Use Git LFS** for any legitimately large files that need versioning

## Total Space Saved: ~30+ MB
