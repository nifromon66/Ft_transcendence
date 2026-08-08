## Overview
- Date : 08/06/2026.
- Start time : 10 AM.
- Launch break : 12 PM - 13h30 PM.
- End time : 17 PM.
- Location : Cantina, 42, Perpignan, France
## Attendance :
- [x] @nifromon
- [x] @juduchar
- [x] @cgregoir
- [x] @shanwang
## Agenda Items :
- Basic Nginx by @cgregoir
- Basic PostGreSQL by @shanwang
- Basic ModSecurity WAF by @nifromon
- Basic File management by @juduchar
- Basic Tailwind CSS setup by @cgregoir (opt after Nginx)
## Notes :

### Items :
- [x] Basic Nginx by @cgregoir
- [x] Basic PosgreSQL by @juduchar
- [] Basic ModSecurity WAF by @nifromon
- [] Basic FIle management by @juduchar
- [] Basic Tailwind CSS setup by @cgregoir

### Merge :
All done works were merged into the test branch then we solved the conflicts and problems that followed to have a working project that we merged into the main branch and from which everyone can merge into their own personal branch and work on their own tasks.

### Envs :
We decided that we needed to have isolated .env files for each services / modules / utilities so that we can modify the whole project from a single entry file.

We did but we encountered some problems with the .conf files (Modsecurity and Nginx) which didn't seem to be able access them. The solution is that we had to first have our own .conf.template files that were then converted to .conf files in the entrypoint.sh of the container using the envsubst utility.
## Action Items :
- Basic Tailwind CSS setup by @cgregoir
- Develop the PostGreSQL database by @shanwang
- Basic File management by @juduchar
- Basic Frontend user log-in/out + profile interface by @juduchar (opt after Basic File Management)
- Basic ModSecurity WAF by @nifromon
