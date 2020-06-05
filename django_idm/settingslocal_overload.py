# PROVISIONING, IF NONE user can set their preferred username without a arbitrary prefix
ACCOUNT_CREATE_USERNAME_PRESET = ('name', 'surname')
ACCOUNT_CREATE_USERNAME_PRESET_SEP = '.'
ACCOUNT_CREATE_USERNAME_SUFFIX = True
ACCOUNT_CREATE_USERNAME_SUFFIX_CUSTOMIZABLE = False
ACCOUNT_CREATE_USERNAME_CREATION_FUNC = 'provisioning.utils.get_available_ldap_usernames'
