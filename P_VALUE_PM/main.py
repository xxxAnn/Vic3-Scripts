import re, os, json

def price(price_dic, goods):
    return sum([int(price_dic[good[0]])*int(good[1]) for good in goods])

pat = re.compile(r'(.*?) = \{(\n|.)*?cost = (.*?)\n(\n|.)*?\}')
pat_lvlscld = re.compile(r'level_scaled = {((\n|.)*?)}')
pat_wrkfcld = re.compile(r'workforce_scaled = {((\n|.)*?)}')
pat_empl = re.compile(r'building_employment_(.*?)_add = (.*?)( |\n)')
pat_input = re.compile(r'building_input_(\_|.*?)_add = (.*?)( |\n)')
pat_output = re.compile(r'building_output_(.*?)_add = (.*?)( |\n)')

with open("config.txt", "r", encoding='utf-8') as f:
    loc = f.readline().replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc2 = f.readlines()[1].replace("\n", "")
    
if __name__ == "__main__":
    with open(loc, "r", encoding='utf-8') as f:
        goods_prices = dict([(x[0], x[2]) for x in pat.findall(f.read())])
        
    g_u_dict = {}

    for n in os.listdir(loc2):
        with open(loc2 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
            m = re.split(r"(pm.*?) = {", raw_txt)[1:]
        
            m = [m[i:i+2] for i in range(0, len(m), 2)]

        with open(loc2 + "\\" + n, "w", encoding='utf-8') as f:
            for pm in m:
                o = 0
                i = 0
                e = 0
                for tx in pat_wrkfcld.findall(pm[1]):
                    o = price(goods_prices, pat_output.findall(tx[0])) 
                    i = price(goods_prices, pat_input.findall(tx[0]))

                o_i = o - i
                for tx in pat_lvlscld.findall(pm[1]):
                    e = sum([int(pop[1]) for pop in pat_empl.findall(tx[0])])
                if e != 0:
                    g_u_dict[pm[0]] = round((52*o_i)/e, 1)
                    raw_txt = re.sub(r"(# p = (.*?), e = (.*?), pe = (.*?)\n)?(.*?){}".format(pm[0]), "# p = {}, e = {}, pe = {}\n{}".format(g_u_dict[pm[0]], e, g_u_dict[pm[0]]*e, pm[0]), raw_txt)
                else:
                    raw_txt = re.sub(r"(# p = (.*?), e = (.*?), pe = (.*?)\n)?(.*?){} =".format(pm[0]), "{} =".format(pm[0]), raw_txt)

            f.write(raw_txt)

    with open("out.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(g_u_dict, indent=4))
