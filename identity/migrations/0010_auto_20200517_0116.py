# Generated by Django 3.0.6 on 2020-05-16 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0009_auto_20200515_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractidentityaddress',
            name='postal_code',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='Postal code'),
        ),
        migrations.AlterField(
            model_name='identity',
            name='affiliation',
            field=models.CharField(choices=[('student,member', 'student [student, member]'), ('member', 'associato (ad es. CNR), consorziato (membro del consorzio a cui l"ente appartiene), dipendente altra università o ente di ricerca o azienda sanitaria/ospedaliera/policlinico, dottorando di altra università (consorziata), laureato frequentatore/collaboratore di ricerca (a titolo gratuito) [member]'), ('', 'cessato'), ('affiliate', 'convenzionato (cliente delle convenzioni), fornitore (dipendente o titolare delle ditte fornitrici), ispettore, ospite / visitatore [affiliate]'), ('staff,member', 'dipendente, professore, ricercatore, titolare di assegno di ricerca, tutor, assistente universitario, collaboratore coordinato continuativo, collaboratore linguistico, cultore della materia [staff, member]'), ('staff,member,student', 'dottorando, specializzando [staff, member, student]'), ('member', 'lettore di scambio, titolare di borsa di studio, volontario servizio civile nazionale [member]'), ('student', 'studente erasmus in ingresso [student]'), ('student,member', 'studente, studente fuori sede (tesista, tirocinante, ...), studente laurea specialistica, studente master, studente siss [member, student]')], help_text='Affiliation', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='identity',
            name='flusso',
            field=models.CharField(choices=[('web', 'web'), ('de-visu', 'de-visu'), ('SPID', 'SPID'), ('import', 'Import')], default='', help_text='How this entry was created in the DB', max_length=135, verbose_name='Flow'),
        ),
    ]
