"# NDC_DTS" 
Dont Forget to install tesseract in the environment path

locate the fieldsets.html at change length_is : '1' to length == '1'
.venv/lib/python3.12/site-packages/jazzmin/templates/admin/includes/fieldset.html

There might be conflicts in SSL / TLS in terms of mailing depending on the device/server configuration
Turn off the failsilently attribute of the send_mail function to view the mailing error
Change tls to ssl
download django ssl
change port
set email use tls to false and set email ssl to true
