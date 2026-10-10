# Example: birthday invitation via template autofill

1. In Canva, open a birthday invitation template (or design your own).
2. Apps → **Data autofill** → tag the headline as `title`, the details as
   `details`, and the photo frame as `photo`. Publish as a brand template
   and copy its ID from the URL.
3. Check the fields:

   ```bash
   canvagen template-fields tmpl_abc123
   ```

4. Generate:

   ```bash
   canvagen autofill tmpl_abc123 --export png --data '{
     "title": "Ava turns seven!",
     "details": "Saturday, Dec 12 · 4 PM · 21 Maple St"
   }'
   ```

   The finished invitation PNG downloads immediately, and the editable design
   stays in your Canva account.
