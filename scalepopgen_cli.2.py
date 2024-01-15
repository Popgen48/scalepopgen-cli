import os
import os.path
import time
import prompt_toolkit
from prompt_toolkit.completion import PathCompleter
from beaupy.spinners import *
from beaupy import confirm, prompt, select
from rich.console import Console
import pyfiglet
import yaml
from yaml.loader import SafeLoader
from workflow_dict import worfklow_dict as dictionary

console = Console()


class util:
    def print_header(self):
        f = pyfiglet.figlet_format("scale popgen", font="starwars")
        print(f)

    def clear_screen(self):
        os.system("clear")

    def read_options(self, dict):
        gpl = []
        for key in dict:
            gpl.append(f"{key}: {dict[key]}")
        gpl.append("back")
        name = select(gpl, cursor="🢧", cursor_style="cyan")
        name = str(name).split(":")[0]
        return name

    def is_file_exit(self, file):
        header = 0
        with open(file) as source:
            for line in source:
                line = line.rstrip().split(",")
                if header == 0:
                    header += 1
                else:
                    if not os.path.isfile(line[1]) or not os.path.isfile(line[2]):
                        console.print(
                            f"[red]vcf or index does not exits for {line}[/red]"
                        )
                        time.sleep(2)

    def read_file_prompt(self, param, help_message, default_param, ext):
        console.print(help_message)
        param_var = param + ":"
        param_f = prompt_toolkit.prompt(
            param_var,
            completer=PathCompleter(),
        )
        if not os.path.isfile(param_f) or not param_f.endswith(ext):
            console.print(
                f"[red]{param_var}{param_f} does not exist or does not end with {ext}[/red]"
            )
            time.sleep(2)
            return default_param
        else:
            self.is_file_exit(param_f) if param == "input" else 23
            return param_f

    def read_string_prompt(self, param, help_message, default_param):
        string_o = default_param
        console.print(help_message)
        param_var = param + ":"
        string_o = prompt(param_var, target_type=str)
        return string_o

    def read_int_prompt(self, param, help_message, default_param, min_i, max_i):
        console.print(help_message)
        param_var = param + ":"
        int_o = float(prompt(param_var))
        if int_o < float(min_i) or int_o > float(max_i):
            console.print(
                f"[red]the parameter {param_var} should be greater than or equal to {min_i} and smaller than or equal to {max_i}[/red]"
            )
            time.sleep(2)
            return default_param
        else:
            return int_o

    def read_bool_confirm(self, param, help_message):
        console.print(help_message)
        param_var = param + " ?:"
        if confirm(param_var):
            return True
        else:
            return False


class ReadYml:
    def __init__(self, yml):
        self.d = dictionary()
        self.param_general = self.d.param_general
        self.param_filtering = self.d.param_filtering
        self.yml = yml

    def set_params(self):
        with open(self.yml, "r") as p:
            yaml_params = yaml.load(p, Loader=SafeLoader)
            for key in self.param_general:
                if key in yaml_params:
                    self.param_general[key] = yaml_params[key]
            for key in self.param_filtering:
                if key in yaml_params:
                    self.param_filtering[key] = yaml_params[key]


class SetGeneralParameters:
    def __init__(self, param_general):
        self.d = dictionary()
        self.u = util()
        self.help_general = self.d.help_general
        self.param_general = param_general

    def print_header(self):
        console.print(f"[yellow]setting the general parameters[/yellow]")

    def main_function(self):
        self.u.print_header()
        self.print_header()
        name = self.u.read_options(self.param_general)
        map_ext_dict = {
            "sample_map": ".map",
            "chrom_length_map": ".map",
            "color_map": ".map",
            "input": ".csv",
            "fasta": ".fna",
        }
        str_list = ["outprefix", "outgroup"]
        while name != "back":
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_general[name],
                    self.param_general[name],
                    map_ext_dict[name],
                )
            if name in str_list:
                update_param = self.u.read_string_prompt(
                    name, self.help_general[name], self.param_general[name]
                )
            if name == "max_chrom":
                update_param = self.u.read_int_prompt(
                    name, self.help_general[name], self.param_general[name], 1, 100
                )
            if name == "allow_extra_chrom":
                update_param = self.u.read_bool_confirm(name, self.help_general[name])
            self.param_general[name] = update_param
            self.u.clear_screen()
            self.u.print_header()
            self.print_header()
            name = self.u.read_options(self.param_general)
        self.u.clear_screen()
        return self.param_general


class SetFilteringParameters:
    def __init__(self, param_filtering):
        self.d = dictionary()
        self.u = util()
        self.help_filtering = self.d.help_filtering
        self.param_filtering = param_filtering

    def print_header(self):
        console.print(
            f"[yellow]setting the parameters for filtering SNPs and samples[/yellow]"
        )

    def main_function(self):
        self.u.print_header()
        self.print_header()
        name = self.u.read_options(self.param_filtering)
        map_ext_dict = {"rem_indi": ".txt", "rem_snps": ".txt"}
        int_param_dict = {
            "mind": [0, 1],
            "king_cutoff": [0, 1],
            "maf": [0, 1],
            "min_meanDP": [0, 9999],
            "max_meanDP": [0, 9999],
            "max_missing": [0, 1],
            "hwe": [0, 1],
            "minQ": [0, 9999],
        }
        bool_list = [
            "apply_indi_filters",
            "apply_snp_filters",
            "indiv_summary",
        ]
        indi_filters = ["rem_indi", "mind", "king_cutoff"]
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_filtering[name],
                    self.param_filtering[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(name, self.help_filtering[name])
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_filtering[name],
                    self.param_filtering[name],
                    map_ext_dict[name],
                )
            self.param_filtering[
                "apply_indi_filters" if name in indi_filters else "apply_snp_filters"
            ] = True
            self.param_filtering[name] = update_param
            self.u.clear_screen()
            self.u.print_header()
            self.print_header()
            name = self.u.read_options(self.param_filtering)
        self.u.clear_screen()
        return self.param_filtering


class ScalepopgenCli:
    def __init__(self):
        self.d = dictionary()
        self.u = util()
        self.param_general = self.d.param_general
        self.param_filtering = self.d.param_filtering

    def read_yaml(self):
        if confirm("read existing yaml file of the parameters?"):
            console.print("[yellow]enter the path to the yaml file[/yellow]")
            yaml_file = prompt_toolkit.prompt("yaml:", completer=PathCompleter())
            spinner_animation = ["▉▉", "▌▐", "  ", "▌▐", "▉▉"]
            spinner = Spinner(spinner_animation, "reading yaml file ...")
            spinner.start()
            time.sleep(2)
            spinner.stop()
            self.y = ReadYml(yaml_file)
            self.y.set_params()
            console.print(
                f"[green]yaml file was read and the parameters have been saved[/green]"
            )
            time.sleep(1)
            self.param_general = self.y.param_general
        os.system("clear")

    def main_function(self):
        self.u.clear_screen()
        self.u.print_header()
        self.read_yaml()
        self.u.print_header()
        analyses = [
            "general settings",
            "filtering",
            "genetic structure workflows",
            "treemix workflow",
            "signatures of selection workflows",
            "save & exit",
        ]
        console.print("Set or view the parameters for:")
        analysis = select(analyses, cursor="🢧", cursor_style="cyan")
        while analysis != "save & exit":
            self.u.clear_screen()
            if analysis == "general settings":
                g = SetGeneralParameters(self.param_general)
                self.param_general = g.main_function()
            if analysis == "filtering":
                f = SetFilteringParameters(self.param_filtering)
                self.param_filtering = f.main_function()
            self.u.print_header()
            analysis = select(analyses, cursor="🢧", cursor_style="cyan")
        self.u.clear_screen()


scalepopgencli = ScalepopgenCli()
scalepopgencli.main_function()
