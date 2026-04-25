@echo off
:: Χρησιμοποιούμε το pythonw για να μην ανοίξει καθόλου παράθυρο τερματικού (silent)
:: Αν δεν υπάρχει το pythonw, θα προσπαθήσει με το κανονικό python αλλά στο background

where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw orchestrator.py
) else (
    start /b python orchestrator.py
)

exit
