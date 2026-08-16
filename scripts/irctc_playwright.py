from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import os
import sys
import time


def automate_irctc():
    url = "https://www.irctc.co.in/nget/train-search"
    with sync_playwright() as p:
        headless_env = os.getenv("PW_HEADLESS", "1")
        headless = not (headless_env == "0" or headless_env.lower() in ("false", "no"))
        browser = p.chromium.launch(headless=headless)
        # create a context with a common user-agent to avoid simple bot detection
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        context = browser.new_context(user_agent=ua, viewport={"width": 1280, "height": 800})
        page = context.new_page()
        print("Opening", url)
        try:
            page.goto(url, wait_until="load", timeout=30000)
        except Exception as e:
            print("Navigation error:", repr(e))
            # try a fallback navigation with a shorter wait
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception as e2:
                print("Fallback navigation error:", repr(e2))
                # continue; later steps will likely fail but we'll log state

        # capture a debug screenshot of the initial page state
        try:
            out_png = os.path.join(os.path.dirname(__file__), "debug_irctc.png")
            page.screenshot(path=out_png, full_page=True)
            print("Saved debug screenshot to", out_png)
        except Exception as e:
            print("Could not take screenshot:", e)
        time.sleep(2)

        # Try to close any modal/popups
        for sel in ["button:has-text('OK')", "button:has-text('Ok')", "button[aria-label='close']"]:
            try:
                btn = page.locator(sel)
                if btn.count() > 0:
                    btn.first.click()
                    print("Closed popup via", sel)
            except Exception:
                pass

        # Handle welcome dialog (e.g., "Welcome to IRCTC") by clicking Yes/I Agree/OK
        try:
            try:
                page.wait_for_selector("text=Welcome", timeout=5000)
                print("Welcome text detected")
            except Exception:
                # continue even if welcome text not detected; still attempt common buttons
                pass

            # If there's a language selection, prefer English and then confirm
            try:
                for eng_sel in ["button:has-text('English')", "text=English"]:
                    try:
                        eng_btn = page.locator(eng_sel)
                        if eng_btn.count() > 0:
                            eng_btn.first.click()
                            print("Clicked language selector via", eng_sel)
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # Click a confirmation button if present (exclude 'Yes')
            for conf_sel in [
                "button:has-text('I Agree')",
                "button:has-text('OK')",
                "button:has-text('Ok')",
                "button:has-text('Continue')",
                "button:has-text('Proceed')",
            ]:
                try:
                    conf_btn = page.locator(conf_sel)
                    if conf_btn.count() > 0:
                        conf_btn.first.click()
                        print("Clicked confirmation via", conf_sel)
                        break
                except Exception:
                    continue
        except Exception as e:
            print("Welcome dialog handling error:", e)

        # Fill source (From) with LTT
        print("Filling source as LTT")
        try:
            # common input placeholders/labels on IRCTC may vary; try a few selectors
            src = page.locator("input[placeholder*='From']")
            if src.count() == 0:
                src = page.locator("input[aria-label*='From']")
            if src.count() == 0:
                src = page.locator("input").nth(0)
            src.fill("LTT")
            time.sleep(1)
            page.keyboard.press("Enter")
        except Exception as e:
            print("Could not fill source:", e)

        # Fill destination (To) with BST
        print("Filling destination as BST")
        try:
            dst = page.locator("input[placeholder*='To']")
            if dst.count() == 0:
                dst = page.locator("input[aria-label*='To']")
            if dst.count() == 0:
                # assume second input
                dst = page.locator("input").nth(1)
            dst.fill("BST")
            time.sleep(1)
            page.keyboard.press("Enter")
        except Exception as e:
            print("Could not fill destination:", e)

        # Click Search
        print("Clicking Search")
        try:
            # try button with text Search
            btn = page.locator("button:has-text('Search')")
            if btn.count() == 0:
                btn = page.locator("button").filter(has_text="Search")
            if btn.count() > 0:
                btn.first.click()
            else:
                # try input[type=submit]
                page.locator("input[type=submit]").first.click()
            time.sleep(3)
        except Exception as e:
            print("Could not click search:", e)

        # Wait for results and find train 22538 or text KUSHINAGAR
        print("Searching for train 22538 / KUSHINAGAR EXP")
        try:
            # try a few text matches
            train_sel = None
            for txt in ["22538", "KUSHINAGAR EXP", "KUSHINAGAR EXP (22538)"]:
                loc = page.locator(f"text=/{txt}/i")
                if loc.count() > 0:
                    train_sel = loc.first
                    break
            if train_sel is None:
                # fallback: search for row containing 22538
                train_sel = page.locator("text=22538")
            if train_sel and train_sel.count() > 0:
                # Click the train row to expand or focus
                train_sel.click()
                print("Clicked train entry")
            else:
                print("Train entry not found; listing text snapshot:")
                print(page.content()[:2000])
        except Exception as e:
            print("Error finding train:", e)

        time.sleep(2)

        # Select date (Tue, 18 Aug) - attempt to click a date button containing '18'
        print("Selecting date 18 Aug")
        try:
            date_button = page.locator("button:has-text('18')")
            if date_button.count() == 0:
                date_button = page.locator("text=18")
            if date_button.count() > 0:
                date_button.first.click()
                print("Clicked date 18")
            else:
                print("Date button not found; skipping explicit date click")
        except Exception as e:
            print("Could not select date:", e)

        time.sleep(1)

        # Click Book Now for that train
        print("Clicking 'Book Now' for selected train (if available)")
        try:
            book_btn = page.locator("button:has-text('Book Now'), text='Book Now'")
            if book_btn.count() == 0:
                book_btn = page.locator("text=Book Now")
            if book_btn.count() > 0:
                book_btn.first.click()
                print("Clicked Book Now")
            else:
                print("'Book Now' button not found in train row")
        except Exception as e:
            print("Could not click Book Now:", e)

        time.sleep(2)

        # Select class: AC First Class (1A)
        print("Selecting class 'AC First Class (1A)'")
        try:
            # Try common selectors: dropdown, radio buttons, or text links
            selected = False
            for sel in [
                "text=AC First Class",
                "text=AC First Class (1A)",
                "text=1A",
                "select",
                "input[type=radio] >> text=1A",
            ]:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0:
                        # If it's a select element, try selecting by visible text
                        tag = loc.evaluate("el => el.tagName")
                        if tag.lower() == "select":
                            try:
                                loc.select_option(label="AC First Class (1A)")
                            except Exception:
                                # try option value fallback
                                loc.select_option(value="1A")
                        else:
                            loc.first.click()
                        selected = True
                        print("Selected class via", sel)
                        break
                except Exception:
                    continue
            if not selected:
                print("Could not find class selector for 1A; continuing")
        except Exception as e:
            print("Error selecting class:", e)

        time.sleep(1)

        # Select date Thu, 20 Aug — click a date labeled '20' (may need month navigation)
        print("Selecting date '20'")
        try:
            date_selected = False
            # try buttons or calendar cells containing '20' and optionally 'Aug'
            for txt in ["20 Aug", "20", "20th"]:
                try:
                    dloc = page.locator(f"button:has-text('{txt}')")
                    if dloc.count() == 0:
                        dloc = page.locator(f"text={txt}")
                    if dloc.count() > 0:
                        dloc.first.click()
                        date_selected = True
                        print("Clicked date via text", txt)
                        break
                except Exception:
                    continue
            if not date_selected:
                print("Date '20' not found; you may need to navigate the calendar manually")
        except Exception as e:
            print("Error selecting date:", e)

        time.sleep(1)

        # Confirm any dialogs with Yes/Confirm
        print("Clicking confirm/Yes dialogs if present")
        try:
            for yes_sel in ["button:has-text('Yes')", "button:has-text('Confirm')", "button:has-text('OK')"]:
                try:
                    yes_btn = page.locator(yes_sel)
                    if yes_btn.count() > 0:
                        yes_btn.first.click()
                        print("Clicked confirmation via", yes_sel)
                        break
                except Exception:
                    continue
        except Exception as e:
            print("Confirmation handling error:", e)

        time.sleep(1)

        # Navigate to sign-in / login page or wait for login modal
        print("Waiting for Sign In / Login prompt (will not enter credentials)")
        try:
            # common login triggers
            login_loc = None
            for txt in ["Login", "Sign In", "Sign In to continue", "Please login"]:
                loc = page.locator(f"text=/{txt}/i")
                if loc.count() > 0:
                    login_loc = loc.first
                    break
            if login_loc:
                try:
                    login_loc.click()
                except Exception:
                    pass
                print("Reached login prompt — please sign in manually in the opened browser window")
            else:
                # fallback: look for navigation to a login URL or form
                if "/login" in page.url or "signin" in page.url.lower():
                    print("Already on a login page:", page.url)
                else:
                    print("Login prompt not detected automatically. Please sign in when ready.")
        except Exception as e:
            print("Error while locating login prompt:", e)

        # If credentials provided via environment variables, attempt to fill and submit the login form.
        user = os.getenv("IRCTC_USER")
        pwd = os.getenv("IRCTC_PASS")
        if user and pwd:
            print("Credentials found in environment — attempting automated sign-in (password will not be logged)")
            try:
                # try multiple selectors to find username field
                username_selectors = [
                    "input[name='username']",
                    "input[name='userId']",
                    "input[id*='user']",
                    "input[placeholder*='User']",
                    "input[aria-label*='User']",
                    "input[type='text']",
                ]
                for sel in username_selectors:
                    try:
                        u = page.locator(sel)
                        if u.count() > 0:
                            u.first.fill(user)
                            print("Filled user id")
                            break
                    except Exception:
                        continue

                # password field
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "input[id*='pass']",
                    "input[placeholder*='Password']",
                ]
                for sel in password_selectors:
                    try:
                        pfield = page.locator(sel)
                        if pfield.count() > 0:
                            pfield.first.fill(pwd)
                            print("Filled password (hidden)")
                            break
                    except Exception:
                        continue

                # submit/login button
                for l in ["button:has-text('Login')", "button:has-text('Sign In')", "button[type='submit']", "input[type='submit']"]:
                    try:
                        btn = page.locator(l)
                        if btn.count() > 0:
                            btn.first.click()
                            print("Clicked login/submit button")
                            break
                    except Exception:
                        continue
            except Exception as e:
                print("Automated login error:", e)

        print("Script completed up to sign-in. Leaving browser open for manual sign-in if headed.")
        # Do not close browser so user can sign in when running headed
        if headless:
            browser.close()


if __name__ == '__main__':
    headed_flag = "--headed"
    if headed_flag in sys.argv:
        os.environ["PW_HEADLESS"] = "0"
    automate_irctc()
