# DailyDictionaryDigest

-   Send out an email with a digest of a random selection of words and their corresponding definitions.

### Intuition

-   A great exercise for perpetual mental acquity and a robust vocabularity

### Notes

-   We build the list of words within python by directly constructing a dictionary from a json file. This is more
    performant than loading a list of new-line-deliminated words.

### Usage

-   In a crontab:

```{bash}
SMTP_HOST=smtp.site.com SMTP_PASS=password EMAIL_FROM=from@test.com EMAIL_TO=to@test.com /thedir/send_digest.py 5
```
