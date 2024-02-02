import os
import os.path
import time
import re
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
    def print_global_header(self):
        f = pyfiglet.figlet_format("scale popgen", font="starwars")
        print(f)

    def print_local_header(self, name):
        console.print(f"[yellow]{name}[/yellow]")
        console.print(f"type n to skip entering any parameter")

    def clear_screen(self):
        os.system("clear")

    def regex_pattern(self, name):
        pattern = "(\[.+?\])(.*)(\[.+?\])(:)(.*)"
        match = re.findall(pattern, name)
        return match[0][1]

    def read_options(self, dict):
        gpl = []
        for key in dict:
            gpl.append(f"[yellow]{key}[/yellow]: [green]{dict[key]}[/green]")
        gpl.append("back")
        name = select(gpl)
        name = str(name) if name == "back" else self.regex_pattern(str(name))
        return name

    def is_file_exist(self, file, default_param):
        lc = 0
        is_vcf = False if file.endswith(".p.csv") else True
        is_vcf_exist = True
        with open(file) as source:
            for line in source:
                line = line.rstrip().split(",")
                if lc == 0:
                    if is_vcf:
                        exp_header = ["chrom", "vcf", "vcf_idx"]
                    else:
                        exp_header = ["prefix", "bed", "bim", "fam"]
                    if exp_header != line:
                        console.print(
                            f'[red]the header should be:{",".join(exp_header)} but it is: {line}[/red]'
                        )
                        time.sleep(1)
                        is_vcf_exist = False
                    lc += 1
                else:
                    if is_vcf:
                        if not os.path.isfile(line[1]) or not os.path.isfile(line[2]):
                            console.print(
                                f"[red]vcf or index does not exits for {line}[/red]"
                            )
                            time.sleep(1)
                            is_vcf_exist = False
                    else:
                        if (
                            not os.path.isfile(line[1])
                            or not os.path.isfile(line[2])
                            or not os.path.isfile(line[3])
                        ):
                            console.print(
                                f"[red].bed, .bim or .fam does not exits for {line}[/red]"
                            )
                            time.sleep(1)
                            is_vcf_exist = False
        return file if is_vcf_exist else default_param

    def read_file_prompt(self, param, help_message, default_param, ext):
        console.print(help_message)
        param_var = param + ":"
        param_f = prompt_toolkit.prompt(
            param_var,
            completer=PathCompleter(),
        )
        if param_f == "n":
            return default_param
        elif not os.path.isfile(param_f) or not param_f.endswith(ext):
            console.print(
                f"[red]{param_var}{param_f} does not exist or does not end with {ext}[/red]"
            )
            time.sleep(1)
            return default_param
        else:
            param_f = (
                self.is_file_exist(param_f, default_param)
                if param == "input"
                else param_f
            )
            param_f = os.path.abspath(str(param_f))
            return param_f

    def read_string_prompt(self, param, help_message, default_param):
        string_o = default_param
        console.print(help_message)
        param_var = param + ":"
        string_o = prompt(param_var, target_type=str)
        return string_o if string_o != "n" else default_param

    def read_string_args_prompt(
        self, param, help_message, default_param, exp_args_list
    ):
        string_o = default_param
        console.print(
            help_message + ", valid arguments are: " + " ".join(exp_args_list)
        )
        param_var = param + ":"
        is_broken = False
        string_o = prompt(param_var, target_type=str)
        if string_o == "n":
            return default_param
        else:
            if param == "beagle5_args":
                pattern = r"([^=\s\s+]+)\="
            else:
                pattern = re.compile(r"[\-A-Za-z]+")
            obs_args_list = re.findall(pattern, string_o)
            for args in obs_args_list:
                if args not in exp_args_list:
                    console.print(
                        f"[red]the parameter {args} is not the expected argument for {param}[/red]"
                    )
                    is_broken = True
                    time.sleep(1)
                    break
            if is_broken:
                return default_param
            else:
                return string_o

    def read_int_prompt(self, param, help_message, default_param, min_i, max_i):
        float_list = [
            "mind",
            "king_cutoff",
            "maf",
            "hwe",
            "max_missing",
            "r2_threshold",
            "perc_threshold",
        ]
        console.print(help_message)
        param_var = param + ":"
        int_o = prompt(param_var)
        if int_o == "n":
            return default_param
        else:
            int_o = int(int_o) if param not in float_list else float(int_o)
            if int_o < float(min_i) or int_o > float(max_i):
                console.print(
                    f"[red]the parameter {param_var} should be greater than or equal to {min_i} and smaller than or equal to {max_i}[/red]"
                )
                time.sleep(1)
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
    def __init__(self, yml, dict_list):
        self.dict_list = dict_list
        self.yml = yml

    def set_params(self):
        with open(self.yml, "r") as p:
            yaml_params = yaml.load(p, Loader=SafeLoader)
            for dict_i in self.dict_list:
                for key in dict_i:
                    if key in yaml_params:
                        dict_i[key] = yaml_params[key]
        return self.dict_list


class SetGeneralParameters:
    def __init__(self, param_general):
        self.d = dictionary()
        self.u = util()
        self.help_general = self.d.help_general
        self.param_general = param_general

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header("setting the general parameters")
        name = self.u.read_options(self.param_general)
        map_ext_dict = {
            "sample_map": ".map",
            "chrom_length_map": ".map",
            "color_map": ".map",
            "input": ".csv",
            "fasta": ".fna",
        }
        int_param_dict = {
            "window_size": [1, 100000000000],
            "step_size": [1, 100000000000],
        }
        str_list = ["outprefix", "outgroup", "outdir"]
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
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_general[name],
                    self.param_general[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name == "allow_extra_chrom":
                update_param = self.u.read_bool_confirm(name, self.help_general[name])
            self.param_general[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header("setting the general parameters")
            name = self.u.read_options(self.param_general)
        self.u.clear_screen()
        return self.param_general


class SetSigSelParam:
    def __init__(
        self,
        param_general_sig_sel,
        param_vcftools_sel,
        param_sweepfinder2,
        param_phasing,
        param_selscan,
    ):
        self.d = dictionary()
        self.u = util()
        self.tool_args = self.d.tool_args
        self.help_general_sig_sel = self.d.help_general_sig_sel
        self.help_vcftools_sel = self.d.help_vcftools_sel
        self.help_sweepfinder2 = self.d.help_sweepfinder2
        self.help_phasing = self.d.help_phasing
        self.help_selscan = self.d.help_selscan
        self.param_general_sig_sel = param_general_sig_sel
        self.param_vcftools_sel = param_vcftools_sel
        self.param_sweepfinder2 = param_sweepfinder2
        self.param_phasing = param_phasing
        self.param_selscan = param_selscan

    def set_param_general_sig_sel(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the general parameters to run signature of selection analyses"
        )
        name = self.u.read_options(self.param_general_sig_sel)
        int_param_dict = {
            "min_sample_size": [1, 99999999],
            "window_size": [1, 100000000000],
            "step_size": [1, 100000000000],
            "perc_threshold": [0, 1],
        }
        bool_list = ["skip_outgroup"]
        map_ext_dict = {
            "skip_pop": ".txt",
            "selection_plot_yml": ".yml",
        }
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_general_sig_sel[name],
                    self.param_general_sig_sel[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_general_sig_sel[name],
                    self.param_general_sig_sel[name],
                    map_ext_dict[name],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_general_sig_sel[name]
                )
            self.param_general_sig_sel[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the general parameters to run signature of selection analyses"
            )
            name = self.u.read_options(self.param_general_sig_sel)
        self.u.clear_screen()

    def set_param_vcftools_sel(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters to run signature of selection analysis using vcftools"
        )
        name = self.u.read_options(self.param_vcftools_sel)
        bool_list = [
            "skip_chromwise",
            "pairwise_local_fst",
            "fst_one_vs_all",
            "tajimas_d",
            "pi_val",
        ]
        while name != "back":
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_vcftools_sel[name]
                )
            self.param_vcftools_sel[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters to run signature of selection analysis using vcftools"
            )
            name = self.u.read_options(self.param_vcftools_sel)
        self.u.clear_screen()

    def set_param_sweepfinder2(self):
        self.u.print_global_header()
        self.u.print_local_header("setting the parameters to run sweepfinder2 workflow")
        name = self.u.read_options(self.param_sweepfinder2)
        bool_list = [
            "sweepfinder2",
            "est_anc_alleles",
        ]
        int_param_dict = {
            "grid_space": [1, 99999999],
            "grid_points": [1, 99999999],
        }
        map_ext_dict = {
            "recomb_map": ".map",
        }
        sweepfinder2_model = ["l", "lr", "s"]
        while name != "back":
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_sweepfinder2[name]
                )
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_sweepfinder2[name],
                    self.param_sweepfinder2[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_sweepfinder2[name],
                    self.param_sweepfinder2[name],
                    map_ext_dict[name],
                )
            if name == "sweepfinder2_model":
                update_param = select(sweepfinder2_model)
            self.param_sweepfinder2[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters to run sweepfinder2 workflow"
            )
            name = self.u.read_options(self.param_sweepfinder2)
        self.u.clear_screen()

    def set_param_phasing(self):
        self.u.print_global_header()
        self.u.print_local_header("setting the parameters for phasing workflow")
        name = self.u.read_options(self.param_phasing)
        bool_list = ["skip_phasing", "beagle5", "impute", "shapeit5"]
        int_param_dict = {
            "burnin": [1, 1000000],
            "iterations": [1, 10000000],
            "ne": [1, 1000000000],
        }
        map_ext_dict = {"phasing_panel": ".map", "phasing_map": ".map"}
        args_list = ["beagle5_args", "shapeit5_args"]
        while name != "back":
            if name in bool_list:
                update_param = self.u.read_bool_confirm(name, self.help_phasing[name])
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_phasing[name],
                    self.param_phasing[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_phasing[name],
                    self.param_phasing[name],
                    map_ext_dict[name],
                )
            if name in args_list:
                update_param = self.u.read_string_args_prompt(
                    name,
                    self.help_phasing[name],
                    self.param_phasing[name],
                    self.tool_args[name],
                )
            self.param_phasing[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header("setting the parameters for phasing workflow")
            name = self.u.read_options(self.param_phasing)
        self.u.clear_screen()

    def set_param_selscan(self):
        self.u.print_global_header()
        self.u.print_local_header("setting the parameters for iHS and XP-EHH workflows")
        name = self.u.read_options(self.param_selscan)
        bool_list = ["ihs", "xpehh"]
        map_ext_dict = {"selscan_map": ".map"}
        args_list = ["ihs_args", "xpehh_args", "ihs_norm_args", "xpehh_norm_args"]
        while name != "back":
            if name in bool_list:
                update_param = self.u.read_bool_confirm(name, self.help_selscan[name])
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_selscan[name],
                    self.param_selscan[name],
                    map_ext_dict[name],
                )
            if name in args_list:
                update_param = self.u.read_string_args_prompt(
                    name,
                    self.help_selscan[name],
                    self.param_selscan[name],
                    self.tool_args[name],
                )
            self.param_selscan[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header("setting the parameters for phasing workflow")
            name = self.u.read_options(self.param_selscan)
        self.u.clear_screen()

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters for running the workflows to identify the signatures of selection"
        )
        analyses = [
            "set the general parameters which are appplicable for all the analyses implemented in this section",
            "set the parameters of the workflows to run vcftools-based analyses (fst, Tajimas'D and pi-values)",
            "set the parameters of the workflow to run sweepfinder2",
            "set the parameters of the workflow to phase the data",
            "set the parameters of the workflows to run selscan-based analyses (iHS, XP-EHH)",
            "back",
        ]
        analysis = select(analyses)
        while str(analysis) != "back":
            self.u.clear_screen()
            if str(analysis) == analyses[0]:
                self.set_param_general_sig_sel()
            if str(analysis) == analyses[1]:
                self.set_param_vcftools_sel()
            if str(analysis) == analyses[2]:
                self.set_param_sweepfinder2()
            if str(analysis) == analyses[3]:
                self.set_param_phasing()
            if str(analysis) == analyses[4]:
                self.set_param_selscan()
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters for running the workflows to identify the signatures of selection"
            )
            analysis = select(analyses)
        self.u.clear_screen()
        return (
            self.param_general_sig_sel,
            self.param_vcftools_sel,
            self.param_sweepfinder2,
            self.param_phasing,
            self.param_selscan,
        )


class SetTreemixParam:
    def __init__(self, param_treemix):
        self.d = dictionary()
        self.u = util()
        self.tool_args = self.d.tool_args
        self.help_treemix = self.d.help_treemix
        self.param_treemix = param_treemix

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters for treemix analysis, note that setting treemix set to false will skip this workflow"
        )
        name = self.u.read_options(self.param_treemix)
        int_param_dict = {
            "k_snps": [1, 10000],
            "n_bootstrap": [1, 10000],
            "n_mig": [0, 1000],
            "n_iter": [0, 1000],
        }
        bool_list = ["treemix", "set_random_seed", "rand_k_snps"]
        args_list = ["treemix_args"]
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_treemix[name],
                    self.param_treemix[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(name, self.help_treemix[name])
            if name in args_list:
                update_param = self.u.read_string_args_prompt(
                    name,
                    self.help_treemix[name],
                    self.param_treemix[name],
                    self.tool_args[name],
                )
            self.param_treemix[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters for treemix analysis, note that setting treemix set to false will skip this workflow"
            )
            name = self.u.read_options(self.param_treemix)
        self.u.clear_screen()
        return self.param_treemix


class SetGeneticStructureParam:
    def __init__(self, param_genetic_structure):
        self.d = dictionary()
        self.u = util()
        self.help_genetic_structure = self.d.help_genetic_structure
        self.param_genetic_structure = param_genetic_structure
        self.tool_args = self.d.tool_args

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters for the analyses to explore genetic structure, note that if genetic_structure is set to false, then all the below-mentioned analyses will be skipped"
        )
        name = self.u.read_options(self.param_genetic_structure)
        map_ext_dict = {
            "rem_indi_structure": ".txt",
            "smartpca_param": ".txt",
            "pca_plot_yml": ".yml",
            "marker_map": ".map",
            "chrom_map": ".map",
            "admixture_colors": ".txt",
            "admixture_plot_yml": ".yml",
            "admixture_plot_pop_order": ".txt",
            "fst_plot_yml": ".yml",
            "ibs_plot_yml": ".yml",
        }
        int_param_dict = {
            "ld_window_size": [1, 10000000],
            "ld_step_size": [1, 10000000],
            "r2_threshold": [0, 1],
            "start_k": [0, 9999],
            "end_k": [0, 9999],
        }
        bool_list = [
            "genetic_structure",
            "ld_filt",
            "smartpca",
            "admixture",
            "pairwise_global_fst",
            "ibs_dist",
        ]
        args_list = ["admixture_args"]
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_genetic_structure[name],
                    self.param_genetic_structure[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_genetic_structure[name],
                    self.param_genetic_structure[name],
                    map_ext_dict[name],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_genetic_structure[name]
                )
            if name in args_list:
                update_param = self.u.read_string_args_prompt(
                    name,
                    self.help_genetic_structure[name],
                    self.param_genetic_structure[name],
                    self.tool_args[name],
                )
            self.param_genetic_structure[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters for the analyses to explore genetic structure, note that if genetic_structure is set to false, then all the below-mentioned analyses will be skipped"
            )
            name = self.u.read_options(self.param_genetic_structure)
        self.u.clear_screen()
        return self.param_genetic_structure


class SetSnpFilteringParam:
    def __init__(self, param_snp_filtering):
        self.d = dictionary()
        self.u = util()
        self.help_snp_filtering = self.d.help_snp_filtering
        self.param_snp_filtering = param_snp_filtering

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters for filtering the SNPs, note that if apply_snp_filters is set to false, then the SNP-filtering step is skipped entirely"
        )
        name = self.u.read_options(self.param_snp_filtering)
        map_ext_dict = {"rem_snps": ".txt"}
        int_param_dict = {
            "maf": [0, 1],
            "min_meanDP": [0, 9999],
            "max_meanDP": [0, 9999],
            "max_missing": [0, 1],
            "hwe": [0, 1],
            "minQ": [0, 9999],
        }
        bool_list = [
            "apply_snp_filters",
        ]
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_snp_filtering[name],
                    self.param_snp_filtering[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_snp_filtering[name]
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_snp_filtering[name],
                    self.param_snp_filtering[name],
                    map_ext_dict[name],
                )
            self.param_snp_filtering[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters for filtering the SNPs, note that if apply_snp_filters is set to false, then the SNP-filtering step is skipped entirely"
            )
            name = self.u.read_options(self.param_snp_filtering)
        self.u.clear_screen()
        return self.param_snp_filtering


class SetIndiFilteringParam:
    def __init__(self, param_indi_filtering):
        self.d = dictionary()
        self.u = util()
        self.help_indi_filtering = self.d.help_indi_filtering
        self.param_indi_filtering = param_indi_filtering

    def main_function(self):
        self.u.print_global_header()
        self.u.print_local_header(
            "setting the parameters for filtering samples, note that if apply_indi_filters is set to false, then the sample-filtering step is skipped entirely"
        )
        name = self.u.read_options(self.param_indi_filtering)
        map_ext_dict = {"rem_indi": ".txt"}
        int_param_dict = {
            "mind": [0, 1],
            "king_cutoff": [0, 1],
        }
        bool_list = [
            "apply_indi_filters",
        ]
        while name != "back":
            if name in int_param_dict:
                update_param = self.u.read_int_prompt(
                    name,
                    self.help_indi_filtering[name],
                    self.param_indi_filtering[name],
                    int_param_dict[name][0],
                    int_param_dict[name][1],
                )
            if name in map_ext_dict:
                update_param = self.u.read_file_prompt(
                    name,
                    self.help_indi_filtering[name],
                    self.param_indi_filtering[name],
                    map_ext_dict[name],
                )
            if name in bool_list:
                update_param = self.u.read_bool_confirm(
                    name, self.help_indi_filtering[name]
                )
            self.param_indi_filtering[name] = update_param
            self.u.clear_screen()
            self.u.print_global_header()
            self.u.print_local_header(
                "setting the parameters for filtering samples, note that if apply_indi_filters is set to false, then the sample-filtering step is skipped entirely"
            )
            name = self.u.read_options(self.param_indi_filtering)
        self.u.clear_screen()
        return self.param_indi_filtering


class ScalepopgenCli:
    def __init__(self):
        self.d = dictionary()
        self.u = util()
        self.dict_list = [dict_i.copy() for dict_i in self.d.dict_list]

    def read_yaml(self):
        if confirm("[yellow]read existing yaml file of the parameters?[/yellow]"):
            console.print(
                "[yellow]enter the path to a yaml file containing parameters or type n to skip this step[/yellow]"
            )
            yaml_file = prompt_toolkit.prompt("yaml:", completer=PathCompleter())
            if yaml_file != "n":
                spinner_animation = ["▉▉", "▌▐", "  ", "▌▐", "▉▉"]
                spinner = Spinner(spinner_animation, "reading yaml file ...")
                spinner.start()
                time.sleep(1)
                spinner.stop()
                y = ReadYml(yaml_file, self.dict_list)
                self.dict_list = y.set_params()
                console.print(
                    f"[green]yaml file was read and the parameters have been saved[/green]"
                )
                time.sleep(1)

        os.system("clear")

    def write_yaml_prompt(self):
        console.print(
            "save output yaml file; the file must end with .yml or .yaml or type n to skip saving the parameter file"
        )
        param_var = "output_yaml" + ":"
        param_f = prompt_toolkit.prompt(
            param_var,
            completer=PathCompleter(),
        )
        while (
            not param_f.endswith(".yml")
            and not param_f.endswith(".yaml")
            and param_f != "n"
        ):
            param_f = prompt_toolkit.prompt(
                param_var,
                completer=PathCompleter(),
            )
        return param_f

    def write_yaml(self, param_f):
        if param_f != "n":
            final_dict = {}
            for i, v in enumerate(self.dict_list):
                v_default = self.d.dict_list[i]
                for key in v:
                    if v[key] != v_default[key]:
                        final_dict[key] = v[key]
            spinner_animation = ["▉▉", "▌▐", "  ", "▌▐", "▉▉"]
            spinner = Spinner(
                spinner_animation,
                "saving yaml file of the non-default parameters ...file saved!",
            )
            spinner.start()
            time.sleep(1)
            spinner.stop()
            with open(param_f, "w") as dest:
                yaml.dump(final_dict, dest)

    def main_function(self):
        self.u.clear_screen()
        self.u.print_global_header()
        self.read_yaml()
        self.u.print_global_header()
        analyses = [
            "the general input, output and other global parameters",
            "the parameters to remove samples",
            "the parameters to remove SNPs",
            "the parameters to explore genetic structure",
            "the parameters for treemix analysis",
            "the parameters to identify signatures of selection",
            "save",
            "exit",
        ]
        console.print("[yellow]Set or view:[/yellow]")
        analysis = select(analyses)
        while analysis != "exit":
            self.u.clear_screen()
            if analysis == analyses[0]:
                g = SetGeneralParameters(self.dict_list[0])
                self.dict_list[0] = g.main_function()
            if analysis == analyses[1]:
                fi = SetIndiFilteringParam(self.dict_list[1])
                self.dict_list[1] = fi.main_function()
            if analysis == analyses[2]:
                fs = SetSnpFilteringParam(self.dict_list[2])
                self.dict_list[2] = fs.main_function()
            if analysis == analyses[3]:
                gs = SetGeneticStructureParam(self.dict_list[3])
                self.dict_list[3] = gs.main_function()
            if analysis == analyses[4]:
                ta = SetTreemixParam(self.dict_list[4])
                self.dict_list[4] = ta.main_function()
            if analysis == analyses[5]:
                sa = SetSigSelParam(
                    self.dict_list[5],
                    self.dict_list[6],
                    self.dict_list[7],
                    self.dict_list[8],
                    self.dict_list[9],
                )
                (
                    self.dict_list[5],
                    self.dict_list[6],
                    self.dict_list[7],
                    self.dict_list[8],
                    self.dict_list[9],
                ) = sa.main_function()
            if analysis == analyses[6]:
                param_f = self.write_yaml_prompt()
                self.write_yaml(param_f)
            self.u.print_global_header()
            console.print("[yellow]Set or view:[/yellow]")
            analysis = select(analyses)
        self.u.clear_screen()


scalepopgencli = ScalepopgenCli()
scalepopgencli.main_function()
