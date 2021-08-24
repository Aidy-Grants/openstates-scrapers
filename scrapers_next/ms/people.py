from spatula import URL, HtmlPage
from openstates.models import ScrapePerson
from itertools import zip_longest
from dataclasses import dataclass
import re

CAP_ADDRESS = """P. O. Box 1018
Jackson, MS 39215"""


@dataclass
class PartialPerson:
    name: str
    title: str
    chamber: str
    source: str


# source https://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class LegDetail(HtmlPage):
    input_type = PartialPerson

    def process_page(self):
        if self.source.url == "http://ltgovhosemann.ms.gov/":
            return None

        district = self.root.cssselect("district")[0].text_content()
        party = self.root.cssselect("party")[0].text_content()

        if party == "D":
            party = "Democratic"
        elif party == "R":
            party = "Republican"
        elif party == "I":
            party = "Independent"

        # no party listed on page
        if self.input.name in ["Lataisha Jackson", "John G. Faulkner"]:
            party = "Democratic"

        p = ScrapePerson(
            name=self.input.name,
            state="ms",
            chamber=self.input.chamber,
            district=district,
            party=party,
        )

        p.add_source(self.input.source)
        p.add_source(self.source.url)
        p.add_link(self.source.url, note="homepage")

        email = self.root.cssselect("email")
        if len(email) > 0:
            email = email[0].text_content().strip()
            if (
                not re.search(r"@senate.ms.gov", email)
                and self.input.chamber == "upper"
            ):
                email = email + "@senate.ms.gov"
            elif (
                not re.search(r"@house.ms.gov", email) and self.input.chamber == "lower"
            ):
                email = email + "@house.ms.gov"
            p.email = email
        img_id = self.root.cssselect("img_name")[0].text_content()
        if self.input.chamber == "upper":
            img = "http://billstatus.ls.state.ms.us/members/senate/" + img_id
        else:
            img = "http://billstatus.ls.state.ms.us/members/house/" + img_id
        p.image = img

        if self.input.title != "member":
            p.extras["title"] = self.input.title

        last_name = self.root.cssselect("u_mem_nam")[0].text_content()
        if re.search(r"\(\d{1,2}[a-z]{2}\)", last_name):
            last_name = re.search(r"(.+)\s\(\d{1,2}[a-z]{2}\)", last_name).groups()[0]
        p.family_name = last_name

        # office = self.root.cssselect("office")[0].text_content()
        # print(office)
        # cong = self.root.cssselect("cong")[0].text_content()
        # print(cong)
        # supreme = self.root.cssselect("supreme")[0].text_content()
        # print(supreme)
        # occupation = self.root.cssselect("occupation")[0].text_content()
        # print(occupation)
        # education1 = self.root.cssselect("education")[0].text_content()
        # print(education1)
        # education2 = self.root.cssselect("education")[1].text_content()
        # print(education2)
        # education3 = self.root.cssselect("education")[2].text_content()
        # print(education3)
        # cnty_info1 = self.root.cssselect("cnty_info")[0].text_content()
        # print(cnty_info1)
        # cnty_info2 = self.root.cssselect("cnty_info")[1].text_content()
        # print(cnty_info2)
        # cnty_info3 = self.root.cssselect("cnty_info")[2].text_content()
        # print(cnty_info3)
        # cnty_info4 = self.root.cssselect("cnty_info")[3].text_content()
        # print(cnty_info4)

        # h_address = self.root.cssselect("h_address")[0].text_content()
        # print(h_address)
        # h_address2 = self.root.cssselect("h_address2")[0].text_content()
        # print(h_address2)
        # h_city = self.root.cssselect("h_city")[0].text_content()
        # print(h_city)
        # h_zip = self.root.cssselect("h_zip")[0].text_content()
        # print(h_zip)
        # h_phone = self.root.cssselect("h_phone")[0].text_content()
        # print(h_phone)

        # b_phone = self.root.cssselect("b_phone")[0].text_content()
        # print(b_phone)

        cap_room = self.root.cssselect("cap_room")[0].text_content().strip()
        if cap_room != "":
            cap_addr = "Room %s\n%s" % (cap_room, CAP_ADDRESS)
        else:
            cap_addr = CAP_ADDRESS
        p.capitol_office.address = cap_addr

        cap_phone = self.root.cssselect("cap_phone")[0].text_content()
        if cap_phone != "":
            p.capitol_office.voice = cap_phone
            print(cap_phone)

        # oth_phone = self.root.cssselect("oth_phone")[0].text_content()
        # print(oth_phone)
        # oth_type = self.root.cssselect("oth_type")[0].text_content()
        # print(oth_type)

        return p


class Legislators(HtmlPage):
    def process_page(self):
        members = self.root.getchildren()
        for member in members:
            children = member.getchildren()
            if children == []:
                continue
            elif len(children) == 3:
                title = children[0].text_content().strip()
                name = children[1].text_content().strip()
                link_id = children[2].text_content().strip()
                if link_id == "http://ltgovhosemann.ms.gov/":
                    link = link_id
                else:
                    link = "http://billstatus.ls.state.ms.us/members/" + link_id

                partial_p = PartialPerson(
                    name=name, title=title, chamber=self.chamber, source=self.source.url
                )

                yield LegDetail(partial_p, source=link)
            else:
                for mem in grouper(member, 3):
                    name = mem[0].text_content().strip()
                    link_id = mem[1].text_content().strip()
                    link = "http://billstatus.ls.state.ms.us/members/" + link_id

                    partial_p = PartialPerson(
                        name=name,
                        title="member",
                        chamber=self.chamber,
                        source=self.source.url,
                    )

                    yield LegDetail(partial_p, source=link)


class Senate(Legislators):
    source = URL("http://billstatus.ls.state.ms.us/members/ss_membs.xml")
    chamber = "upper"


class House(Legislators):
    source = URL("http://billstatus.ls.state.ms.us/members/hr_membs.xml")
    chamber = "lower"
