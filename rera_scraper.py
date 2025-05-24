import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedOdishaRERAScaper:
    def __init__(self, chromedriver_path):
        self.chromedriver_path = chromedriver_path
        self.driver = None
        self.base_url = "https://rera.odisha.gov.in/projects/project-list"
        self.projects_data = []
        self.wait = None

    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 15)

            logger.info("✅ Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome WebDriver: {str(e)}")
            return False

    def wait_for_page_load(self, timeout=15):
        """Enhanced page load waiting with multiple checks"""
        try:
            # Wait for body
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Wait for any loading indicators to disappear
            loading_selectors = [
                ".loading", ".spinner", "[class*='loading']",
                ".loader", "[class*='loader']", "#loading"
            ]

            for selector in loading_selectors:
                try:
                    WebDriverWait(self.driver, 3).until_not(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                except:
                    pass

            # Additional wait for dynamic content
            time.sleep(3)

            # Wait for JavaScript to complete
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        except TimeoutException:
            logger.warning("⚠️ Page load timeout, proceeding anyway")

    def find_view_details_elements(self):
        """Enhanced element finding with multiple strategies"""
        strategies = [
            # XPath strategies
            "//a[contains(text(), 'View Details')]",
            "//button[contains(text(), 'View Details')]",
            "//a[contains(text(), 'View')]",
            "//input[@value='View Details']",
            "//a[contains(@onclick, 'view') or contains(@onclick, 'detail')]",

            # CSS strategies
            "a[href*='view']",
            "a[href*='detail']",
            ".view-btn", ".detail-btn", ".btn-view",
            "button[onclick*='view']"
        ]

        for strategy in strategies:
            try:
                if strategy.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, strategy)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, strategy)

                if elements:
                    logger.info(f"✅ Found {len(elements)} elements using: {strategy}")
                    return elements[:6]

            except Exception as e:
                logger.debug(f"Strategy failed: {strategy} - {str(e)}")
                continue

        return []

    def extract_with_multiple_selectors(self, selectors, field_name):
        """Extract data using multiple selector strategies"""
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    text = element.text.strip()
                    if text and text.lower() not in ['not available', 'n/a', '-', '']:
                        logger.info(f"✅ Found {field_name}: {text}")
                        return text

            except Exception as e:
                logger.debug(f"Selector failed for {field_name}: {selector} - {str(e)}")
                continue

        return "Not Available"

    def click_promoter_tab(self):
        """FIXED: Enhanced promoter tab clicking with better selectors"""
        # More comprehensive tab selectors including variations
        tab_selectors = [
            "//a[contains(text(), 'Promoter Details')]",
            "//a[contains(text(), 'Promoter')]",
            "//button[contains(text(), 'Promoter Details')]",
            "//button[contains(text(), 'Promoter')]",
            "//li[contains(text(), 'Promoter Details')]",
            "//li[contains(text(), 'Promoter')]",
            "//span[contains(text(), 'Promoter Details')]",
            "//span[contains(text(), 'Promoter')]",
            "//*[@id='promoter-tab']",
            "//*[@href='#promoter']",
            "//*[@href='#promoter-details']",
            "//*[contains(@class, 'promoter')]",
            "a[href*='promoter']",
            ".nav-link[href*='promoter']",
            "#promoter-tab",
            ".tab[data-target*='promoter']",
            "button[data-toggle='tab'][href*='promoter']"
        ]

        for selector in tab_selectors:
            try:
                if selector.startswith("//"):
                    tabs = self.driver.find_elements(By.XPATH, selector)
                else:
                    tabs = self.driver.find_elements(By.CSS_SELECTOR, selector)

                for tab in tabs:
                    if tab and tab.is_displayed():
                        try:
                            # Scroll to element
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", tab)
                            time.sleep(1)

                            # Try clicking
                            tab.click()
                            time.sleep(3)
                            logger.info("✅ Successfully clicked Promoter Details tab")
                            return True
                        except:
                            continue

            except Exception as e:
                logger.debug(f"Tab selector failed: {selector} - {str(e)}")
                continue

        logger.warning("⚠️ Could not find or click Promoter Details tab")
        return False

    def extract_project_details(self):
        """FIXED: Enhanced project details extraction with better selectors"""
        project_data = {
            'Rera Regd. No': '',
            'Project Name': '',
            'Promoter Name': '',
            'Address of the Promoter': '',
            'GST No': ''
        }

        try:
            self.wait_for_page_load()

            # Get page source for BeautifulSoup parsing as backup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # FIXED: Extract RERA Registration Number
            rera_selectors = [
                "//td[contains(text(), 'RERA Registration No') or contains(text(), 'RERA Regd. No') or contains(text(), 'Registration No')]/following-sibling::td[1]",
                "//th[contains(text(), 'RERA Registration No') or contains(text(), 'RERA Regd. No') or contains(text(), 'Registration No')]/following-sibling::td[1]",
                "//tr[td[contains(text(), 'RERA Registration No') or contains(text(), 'RERA Regd. No') or contains(text(), 'Registration No')]]/td[2]",
                "//label[contains(text(), 'RERA')]/following-sibling::*[1]",
                "//strong[contains(text(), 'RERA')]/parent::*/following-sibling::*[1]",
                "//*[contains(@class, 'rera-no')]",
                "//*[@id='rera_no' or @id='registration_no']",
                ".registration-number", ".rera-number"
            ]
            project_data['Rera Regd. No'] = self.extract_with_multiple_selectors(rera_selectors, "RERA No")

            # FIXED: Extract Project Name - look for actual project names, not numbers
            name_selectors = [
                # Look in table cells first
                "//td[contains(text(), 'Project Name')]/following-sibling::td[1]",
                "//th[contains(text(), 'Project Name')]/following-sibling::td[1]",
                "//tr[td[contains(text(), 'Project Name')]]/td[2]",

                # Look for headings that are NOT numbers and NOT generic terms
                "//h1[not(contains(text(), 'RERA')) and not(contains(text(), 'Project List')) and not(contains(text(), 'Projects')) and not(number(text())=text())]",
                "//h2[not(contains(text(), 'RERA')) and not(contains(text(), 'Project List')) and not(contains(text(), 'Projects')) and not(number(text())=text())]",
                "//h3[not(contains(text(), 'RERA')) and not(contains(text(), 'Project List')) and not(contains(text(), 'Projects')) and not(number(text())=text())]",

                # Look for specific project name patterns
                "//*[contains(text(), 'Enclave') or contains(text(), 'Residency') or contains(text(), 'Manor') or contains(text(), 'Villa') or contains(text(), 'Heights') or contains(text(), 'Park') or contains(text(), 'Garden') or contains(text(), 'Tower') or contains(text(), 'Plaza') or contains(text(), 'City') or contains(text(), 'Colony') or contains(text(), 'UDYAYEEN') or contains(text(), 'BARSANA') or contains(text(), 'KRISHNA') or contains(text(), 'BHAVYAVILLA')]",

                "//*[contains(@class, 'project-name')]",
                "//*[@id='project_name']",
                ".project-title", ".project-heading"
            ]

            # Custom extraction for project name to filter out numbers
            project_name = "Not Available"
            for selector in name_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        text = element.text.strip()
                        # Filter out numbers, generic terms, and short strings
                        if (text and
                                not text.isdigit() and  # Not a pure number
                                text.lower() not in ['projects', 'project', 'not available', 'n/a', '-', '', 'rera',
                                                     'registration'] and
                                len(text) > 2 and
                                not text.startswith('http')):
                            logger.info(f"✅ Found Project Name: {text}")
                            project_name = text
                            break

                    if project_name != "Not Available":
                        break

                except Exception as e:
                    logger.debug(f"Project name selector failed: {selector} - {str(e)}")
                    continue

            project_data['Project Name'] = project_name

            # Click on Promoter Details tab
            self.click_promoter_tab()

            # FIXED: Extract Promoter Name - handle both "Promoter Name" and "Proprietory Name"
            promoter_selectors = [
                "//td[contains(text(), 'Company Name') or contains(text(), 'Promoter Name') or contains(text(), 'Proprietory Name') or contains(text(), 'Propietory Name') or contains(text(), 'Firm Name')]/following-sibling::td[1]",
                "//th[contains(text(), 'Company Name') or contains(text(), 'Promoter Name') or contains(text(), 'Proprietory Name') or contains(text(), 'Propietory Name')]/following-sibling::td[1]",
                "//tr[td[contains(text(), 'Company Name') or contains(text(), 'Promoter Name') or contains(text(), 'Proprietory Name') or contains(text(), 'Propietory Name')]]/td[2]",
                "//label[contains(text(), 'Company') or contains(text(), 'Promoter') or contains(text(), 'Proprietory') or contains(text(), 'Propietory')]/following-sibling::*[1]",
                "//*[contains(@class, 'promoter-name') or contains(@class, 'company-name')]",
                "//*[@id='company_name' or @id='promoter_name']",
                ".company-name", ".promoter-name", ".firm-name"
            ]

            project_data['Promoter Name'] = self.extract_with_multiple_selectors(promoter_selectors, "Promoter Name")

            # Extract Promoter Address
            address_selectors = [
                "//td[contains(text(), 'Registered Office') or contains(text(), 'Address') or contains(text(), 'Office Address')]/following-sibling::td[1]",
                "//th[contains(text(), 'Registered Office') or contains(text(), 'Address')]/following-sibling::td[1]",
                "//tr[td[contains(text(), 'Registered Office') or contains(text(), 'Address')]]/td[2]",
                "//label[contains(text(), 'Registered Office') or contains(text(), 'Address')]/following-sibling::*[1]",
                "//*[contains(@class, 'promoter-address') or contains(@class, 'office-address')]",
                "//*[@id='registered_address' or @id='office_address']",
                ".registered-address", ".office-address", ".promoter-address"
            ]
            project_data['Address of the Promoter'] = self.extract_with_multiple_selectors(address_selectors, "Address")

            # Extract GST Number
            gst_selectors = [
                "//td[contains(text(), 'GST') or contains(text(), 'GSTIN')]/following-sibling::td[1]",
                "//th[contains(text(), 'GST') or contains(text(), 'GSTIN')]/following-sibling::td[1]",
                "//tr[td[contains(text(), 'GST') or contains(text(), 'GSTIN')]]/td[2]",
                "//label[contains(text(), 'GST') or contains(text(), 'GSTIN')]/following-sibling::*[1]",
                "//*[contains(@class, 'gst-number') or contains(@class, 'gstin')]",
                "//*[@id='gst_no' or @id='gstin']",
                ".gst-number", ".gstin"
            ]
            project_data['GST No'] = self.extract_with_multiple_selectors(gst_selectors, "GST No")

            # Clean up data
            for key, value in project_data.items():
                if isinstance(value, str):
                    # Remove extra commas and clean up
                    cleaned_value = value.replace(',,,,,', '').replace(',,', ',').strip()
                    if cleaned_value.endswith(','):
                        cleaned_value = cleaned_value[:-1]
                    project_data[key] = cleaned_value if cleaned_value else "Not Available"

            return project_data

        except Exception as e:
            logger.error(f"❌ Error extracting project details: {str(e)}")
            return {key: 'Not Available' for key in project_data.keys()}

    def click_view_details_by_index(self, index):
        """Enhanced view details clicking with better error handling"""
        try:
            # Navigate back to main page
            self.driver.get(self.base_url)
            self.wait_for_page_load()

            # Re-find elements
            view_details_elements = self.find_view_details_elements()

            if not view_details_elements or len(view_details_elements) <= index:
                logger.error(f"❌ Could not find View Details element at index {index}")
                return False

            element = view_details_elements[index]

            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(2)

            # Try multiple click methods
            click_methods = [
                lambda: element.click(),
                lambda: self.driver.execute_script("arguments[0].click();", element),
                lambda: ActionChains(self.driver).move_to_element(element).click().perform(),
            ]

            for i, method in enumerate(click_methods):
                try:
                    method()
                    time.sleep(3)

                    # Check if navigation was successful
                    current_url = self.driver.current_url
                    if current_url != self.base_url or len(self.driver.window_handles) > 1:
                        logger.info(f"✅ Successfully clicked View Details for project {index + 1}")
                        return True

                except Exception as click_error:
                    logger.debug(f"Click method {i + 1} failed: {str(click_error)}")
                    continue

            # Try direct navigation if href is available
            try:
                href = element.get_attribute('href')
                if href and href not in ['javascript:void(0)', '#', '']:
                    logger.info(f"🔗 Navigating directly to: {href}")
                    self.driver.get(href)
                    time.sleep(3)
                    return True
            except:
                pass

            return False

        except Exception as e:
            logger.error(f"❌ Error clicking view details for index {index}: {str(e)}")
            return False

    def scrape_projects(self):
        """Main scraping function with enhanced error handling"""
        if not self.setup_driver():
            return False

        try:
            logger.info("🚀 Starting to scrape projects...")
            self.driver.get(self.base_url)
            self.wait_for_page_load()

            # Find available projects
            view_details_elements = self.find_view_details_elements()
            if not view_details_elements:
                logger.error("❌ No projects found on the page")
                return False

            num_projects = min(6, len(view_details_elements))
            logger.info(f"📋 Found {len(view_details_elements)} projects, will scrape {num_projects}")

            # Process each project
            for i in range(num_projects):
                try:
                    logger.info(f"🔄 Processing project {i + 1}/{num_projects}")

                    main_window = self.driver.current_window_handle

                    if self.click_view_details_by_index(i):
                        # Handle new window if opened
                        if len(self.driver.window_handles) > 1:
                            for handle in self.driver.window_handles:
                                if handle != main_window:
                                    self.driver.switch_to.window(handle)
                                    break

                        # Extract project details
                        project_data = self.extract_project_details()
                        self.projects_data.append(project_data)

                        # Close new window if opened
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(main_window)

                    else:
                        logger.warning(f"⚠️ Could not access details for project {i + 1}")
                        # Add placeholder data
                        placeholder_data = {key: 'Not Available' for key in
                                            ['Rera Regd. No', 'Project Name', 'Promoter Name',
                                             'Address of the Promoter', 'GST No']}
                        self.projects_data.append(placeholder_data)

                    time.sleep(2)  # Be respectful to the server

                except Exception as e:
                    logger.error(f"❌ Error processing project {i + 1}: {str(e)}")
                    # Add error data entry
                    error_data = {key: 'Error' for key in
                                  ['Rera Regd. No', 'Project Name', 'Promoter Name',
                                   'Address of the Promoter', 'GST No']}
                    self.projects_data.append(error_data)
                    continue

            return True

        except Exception as e:
            logger.error(f"❌ Error in main scraping function: {str(e)}")
            return False

        finally:
            if self.driver:
                self.driver.quit()

    def save_to_excel(self, filename="odisha_rera_projects_fixed.xlsx"):
        """Save data to Excel with enhanced formatting"""
        try:
            if not self.projects_data:
                logger.warning("⚠️ No data to save")
                return False

            df = pd.DataFrame(self.projects_data)

            # Create Excel writer with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='RERA Projects', index=False)

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['RERA Projects']

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"✅ Data saved to {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving to Excel: {str(e)}")
            return False

    def save_to_csv(self, filename="odisha_rera_projects_fixed.csv"):
        """Save data to CSV with proper formatting"""
        try:
            if not self.projects_data:
                logger.warning("⚠️ No data to save")
                return False

            df = pd.DataFrame(self.projects_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"✅ Data saved to {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving to CSV: {str(e)}")
            return False

    def save_to_json(self, filename="odisha_rera_projects_fixed.json"):
        """Save data to JSON format"""
        try:
            if not self.projects_data:
                logger.warning("⚠️ No data to save")
                return False

            output_data = {
                "scrape_timestamp": datetime.now().isoformat(),
                "total_projects": len(self.projects_data),
                "projects": self.projects_data
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Data saved to {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {str(e)}")
            return False

    def print_results(self):
        """Print results with enhanced formatting"""
        if not self.projects_data:
            print("❌ No data scraped")
            return

        print("\n" + "=" * 100)
        print("🏢 ODISHA RERA PROJECTS - FIXED SCRAPER RESULTS")
        print("=" * 100)
        print(f"📊 Total Projects Scraped: {len(self.projects_data)}")
        print(f"🕐 Scrape Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

        for i, project in enumerate(self.projects_data, 1):
            print(f"\n🏗️  PROJECT {i}")
            print("-" * 60)

            for key, value in project.items():
                # Add emoji indicators
                emoji_map = {
                    'Rera Regd. No': '🆔',
                    'Project Name': '🏢',
                    'Promoter Name': '👤',
                    'Address of the Promoter': '📍',
                    'GST No': '💼'
                }

                emoji = emoji_map.get(key, '📄')
                status = "✅" if value != "Not Available" and value != "Error" else "❌"

                print(f"{emoji} {key:<25}: {status} {value}")

        # Print summary statistics
        print("\n" + "=" * 100)
        print("📈 EXTRACTION SUMMARY")
        print("=" * 100)

        fields = ['Rera Regd. No', 'Project Name', 'Promoter Name', 'Address of the Promoter', 'GST No']
        for field in fields:
            available_count = sum(1 for project in self.projects_data
                                  if project.get(field, 'Not Available') not in ['Not Available', 'Error'])
            percentage = (available_count / len(self.projects_data)) * 100 if self.projects_data else 0
            print(f"{field:<30}: {available_count}/{len(self.projects_data)} ({percentage:.1f}%)")


def main():
    """Main execution function"""
    # Chrome WebDriver path - UPDATE THIS PATH
    CHROMEDRIVER_PATH = "/Users/jhanaviagarwal/Downloads/chromedriver-mac-arm64/chromedriver"

    print("🚀 FIXED Odisha RERA Projects Scraper")
    print("=" * 60)

    # Create scraper instance
    scraper = EnhancedOdishaRERAScaper(CHROMEDRIVER_PATH)

    # Start scraping
    success = scraper.scrape_projects()

    if success:
        # Print results with enhanced formatting
        scraper.print_results()

        # Save to multiple formats
        scraper.save_to_excel()
        scraper.save_to_csv()
        scraper.save_to_json()

        print(f"\n🎉 Scraping completed successfully!")
        print(f"📁 Files saved:")
        print("   📊 odisha_rera_projects_fixed.xlsx")
        print("   📄 odisha_rera_projects_fixed.csv")
        print("   🔗 odisha_rera_projects_fixed.json")
        print("   📋 scraper.log")
    else:
        print("❌ Scraping failed. Check scraper.log for details.")


if __name__ == "__main__":
    main()

