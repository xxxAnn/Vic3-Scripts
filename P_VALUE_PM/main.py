import re

def price(price_dic, goods):
    return sum([int(price_dic[good[0]])*int(good[1]) for good in goods])

pat = re.compile(r'(.*?) = \{(\n|.)*?cost = (.*?)\n(\n|.)*?\}')
pat_input = re.compile(r'building_input_(.*?)_add = (.*?)\n')
pat_output = re.compile(r'building_output_(.*?)_add = (.*?)\n')
pat_empl = re.compile(r'building_employment_(.*?)_add = (.*?)\n')

with open("config.txt", "r", encoding='utf-8') as f:
    loc = f.readline().replace("\n", "")

if __name__ == "__main__":
    with open(loc, "r", encoding='utf-8') as f:
        goods_prices = dict([(x[0], x[2]) for x in pat.findall(f.read())])
    with open("production_method", "r", encoding='utf-8') as f:
        pm_raw_text = f.read()
        inp = pat_input.findall(pm_raw_text)
        out = pat_output.findall(pm_raw_text)
        employee_num = sum([int(pop_type[1]) for pop_type in pat_empl.findall(pm_raw_text)])

    print("The p value is {}".format(52*(price(goods_prices, out) - price(goods_prices, inp))/employee_num))
