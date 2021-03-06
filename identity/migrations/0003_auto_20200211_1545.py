# Generated by Django 2.2.10 on 2020-02-11 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0002_auto_20190219_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identity',
            name='affiliation',
            field=models.CharField(choices=[('student,member', 'studente [student, member]'), ('member', "associato (ad es. CNR), consorziato (membro del consorzio a cui l'ente appartiene), dipendente altra università o ente di ricerca o azienda sanitaria/ospedaliera/policlinico, dottorando di altra università (consorziata), laureato frequentatore/collaboratore di ricerca (a titolo gratuito) [member]"), ('', 'cessato'), ('affiliate', 'convenzionato (cliente delle convenzioni), fornitore (dipendente o titolare delle ditte fornitrici), ispettore, ospite / visitatore [affiliate]'), ('staff,member', 'dipendente, professore, ricercatore, titolare di assegno di ricerca, tutor, assistente universitario, collaboratore coordinato continuativo, collaboratore linguistico, cultore della materia [staff, member]'), ('staff,member,student', 'dottorando, specializzando [staff, member, student]'), ('member', 'lettore di scambio, titolare di borsa di studio, volontario servizio civile nazionale [member]'), ('student', 'studente erasmus in ingresso [student]'), ('student,member', 'studente, studente fuori sede (tesista, tirocinante, ...), studente laurea specialistica, studente master, studente siss [member, student]')], default='studente [student, member]', help_text='Affiliation', max_length=128, null=True),
        ),
    ]
