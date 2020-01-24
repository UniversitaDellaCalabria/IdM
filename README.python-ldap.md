````
import ldap
con = ldap.initialize('ldaps://ldap.testunical.it')
con.simple_bind_s('cn=admin,dc=testunical,dc=it', 'slapdsecret')
results = con.search_s('uid=df,ou=people,dc=testunical,dc=it', ldap.SCOPE_SUBTREE, "objectclass=*")
# or
results = con.search_s('ou=people,dc=testunical,dc=it', ldap.SCOPE_SUBTREE, "(uid=df)")
results

# case filter options
# case insensitive and other
# https://stackoverflow.com/questions/25290494/case-insensitive-substring-ldap-search-on-openldap-2-4-33
````
