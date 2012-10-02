"Google Chrome"

install_trusted_key('https://dl-ssl.google.com/linux/linux_signing_key.pub') # 'wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -'
add_repo('http://dl.google.com/linux/chrome/deb/ stable main', 'google.list')# """sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'"""
update_package_index() # 'sudo apt-get update'
install_package('google-chrome-stable')
