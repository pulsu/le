template_config = """
domains = %(host)s
rsa-key-size = %(bits)s
server = https://acme-v01.api.letsencrypt.org/directory
email = someaddresslike-webmaster@xrstf.de
text = True
renew-by-default = True
authenticator = webroot
webroot-path = /var/www/html
"""

dhparam_4096_body = """-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA7bYwryx9zuva7cABzC26gzYaiiQp/A8Lpqv5SuEWou7YT4CIcqlR
EBICNBUsIAFMwNegRemsy5IKBFU2fhqfMYx9qNIcyfiC9rgMObbfQmxmlXXk6B+P
HbSpgj3FcU5ahugp4OywNCAFLKjmmSyahm7/93ms39m3erTMCdIbtHleAIF5vuDT
CP78WA9HzE7KSUQrYksUiGrQcoHgJyRL0rlTTOW8bA+jmvLjLAnEavA+t3mpPKh8
Deo3tLSXuEmlstN+5uN603kMDX/TbOFyY9U32mSxtEJrxGriryUxXU5KCfrTNFnv
zVt/Opzt15rBxTvjOFRwhlwRc9wZyCcY8wIBAg==
-----END DH PARAMETERS-----
"""

dhparam_2048_body = """-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA7bYwryx9zuva7cABzC26gzYaiiQp/A8Lpqv5SuEWou7YT4CIcqlR
EBICNBUsIAFMwNegRemsy5IKBFU2fhqfMYx9qNIcyfiC9rgMObbfQmxmlXXk6B+P
HbSpgj3FcU5ahugp4OywNCAFLKjmmSyahm7/93ms39m3erTMCdIbtHleAIF5vuDT
CP78WA9HzE7KSUQrYksUiGrQcoHgJyRL0rlTTOW8bA+jmvLjLAnEavA+t3mpPKh8
Deo3tLSXuEmlstN+5uN603kMDX/TbOFyY9U32mSxtEJrxGriryUxXU5KCfrTNFnv
zVt/Opzt15rBxTvjOFRwhlwRc9wZyCcY8wIBAg==
-----END DH PARAMETERS-----
"""