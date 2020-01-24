
### Open DEV tasks

- [Password encoding](https://github.com/django-ldapdb/django-ldapdb/issues/116)

- [LDAP fallback timeout connections](https://github.com/django-ldapdb/django-ldapdb/issues/80)

- [Save entry with any changes trows exception!](https://github.com/django-ldapdb/django-ldapdb/issues/153)

### Fixed bug with PR

- [Search admin BUG for ListField and MultiValueField](https://github.com/django-ldapdb/django-ldapdb/issues/104)

### Fixed bug in ldap_people app

Code aligned for ldap timestamp format. Works!

- [Date and DateTime Field](https://github.com/django-ldapdb/django-ldapdb/issues/149)
  [PR #150](https://github.com/django-ldapdb/django-ldapdb/pull/150)
  [PR #130 DEPRECATED](https://github.com/django-ldapdb/django-ldapdb/pull/130)


### Cross ForeignKey strategy

````
class CrossDbForeignKey(models.ForeignKey):
    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(models.ForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        # Here is the trick, get db relating to fk, not to root model
        using = router.db_for_read(self.rel.to, instance=model_instance)

        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})


class Membership(models.Model):
    member = CrossDbForeignKey(LdapUser)

````


### LOCALE

````
mkdir -p locale

python manage.py makemessages --locale=en
python manage.py compilemessages
````
