import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
import geopandas as gpd
import plotly.graph_objects as go

class Data:
    def __init__(self):

        # Convert shares to totals
        self.ncqg = 300
        
        # Get contributions
        self.contributions_all = pd.read_csv("Robust_Contributions_NCQG_UMIC.csv")
        self.contributions_all_usa = pd.read_csv("Robust_Contributions_NCQG_UMIC_US.csv")
        self.contributions_hic = pd.read_csv("Robust_Contributions_NCQG.csv")
        self.contributions_hic_usa = pd.read_csv("Robust_Contributions_NCQG_US.csv")
        self.contributions = self.collate_contributions()

        
        # Get allocations
        self.allocations = pd.read_csv("Robust_Allocations_NCQG.csv")
        self.allocations["Robust_Share"] = self.allocations["Robust_Share"] * self.ncqg

        # Get regions
        self.regions = pd.read_csv("./DATA/country_mapping.csv")
       

        


    def collate_contributions(self):
        
        robust_all = self.contributions_all[["Country", "ISO", "Region", "Robust_Contribution"]]
        robust_all_usa = self.contributions_all_usa[["Country", "ISO", "Region", "Robust_Contribution"]]
        robust_hic = self.contributions_hic[["Country", "ISO", "Region", "Robust_Contribution"]]
        robust_hic_us = self.contributions_hic_usa[["Country", "ISO", "Region", "Robust_Contribution"]]

        # For all dataframes
        for data in [robust_all, robust_all_usa, robust_hic,robust_hic_us]:
            data["Robust_Contribution"] = data["Robust_Contribution"] * self.ncqg

        collated_robust = robust_all_usa.merge(robust_hic.rename(columns={"Robust_Contribution":"HIC_No_US"}),how="left", 
                                           on=["Country", "ISO", "Region"]).merge(robust_hic_us.rename(columns={"Robust_Contribution":"HIC"}),how="left", 
                                           on=["Country", "ISO", "Region"]).merge(robust_all.rename(columns={"Robust_Contribution":"UMIC_No_US"}),how="left", 
                                           on=["Country", "ISO", "Region"])
        
        return collated_robust

    def produce_contributions_figure(self):

        contributions = self.contributions
        regions = contributions.copy().drop(columns=["Country", "ISO"]).groupby([ "Region"]).agg("sum").reset_index().sort_values(by="Robust_Contribution", ascending=False)

        # Filter contributions
        contributions.sort_values(by="Robust_Contribution", ascending=False)

        # Produce figure
        cmap = "YlGnBu"
        self.plot_map_and_top20(contributions, value_col="HIC", cmap=cmap, savepath="Contributions_HIC", label="All Annex II countries")
        self.plot_map_and_top20(contributions, value_col="HIC_No_US", cmap=cmap, savepath="Contributions_HIC_NO_USA", label="All Annex II countries (exc. USA)")
        self.plot_map_and_top20(contributions, value_col="Robust_Contribution", cmap=cmap, savepath="Contributions_UMIC", label="All UMIC countries")
        self.plot_map_and_top20(contributions, value_col="UMIC_No_US", cmap=cmap, savepath="Contributions_UMIC_NO_USA", label="All UMIC countries (exc. USA)")

        # Produce distributions
        allocations = self.allocations
        cmap = "YlGnBu"
        self.plot_map_and_top20_allocations(allocations, value_col="Robust_Share", cmap="YlOrRd", 
                                savepath="Distributions", label="")



            

    def plot_map_and_top20(self,
                            df: pd.DataFrame,
                            value_col: str,
                            cmap: str,
                            savepath: str,
                            label: str,
                            dpi=300):
        """
        Helper that draws:
          - Top: global choropleth map of contributions in `value_col` with colorbar
          - Bottom: top-20 horizontal bar chart for `value_col`

        Args:
            df: DataFrame with columns ['ISO', 'Country', value_col]
            value_col: name of the contribution column to visualize
            cmap: matplotlib colormap
            savepath: file path to save the figure
            dpi: output resolution
        """
        # Load Natural Earth lowres polygons and join by ISO3
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)


        plot_df = world.merge(
            df[['ISO', 'Country', value_col]],
            left_on='ADM0_A3',
            right_on="ISO",
            how='left'
        )
        
        # Determine color scaling
        data_series = df[value_col].dropna()
        if data_series.empty:
            raise ValueError(f"No data available in column '{value_col}' to plot.")
        vmin = float(data_series.min())
        vmax = 30
        if vmin == vmax:
            # Avoid zero range; expand slightly
            vmin = vmin - 1e-9
            vmax = vmax + 1e-9

        cmap_obj = get_cmap(cmap)
        norm = Normalize(vmin=0, vmax=vmax)

        # Figure layout
        fig = plt.figure(figsize=(10, 25))
        gs = GridSpec(nrows=2, ncols=1, height_ratios=[1, 1], hspace=-0.25)
        ax_map = fig.add_subplot(gs[0, 0])
        ax_bar = fig.add_subplot(gs[1, 0])

        # Plot world choropleth
        plot_df.plot(
            column=value_col,
            ax=ax_map,
            cmap=cmap_obj,
            vmin=0,
            vmax=vmax,
            linewidth=0.2,
            edgecolor='white',
            missing_kwds={'color': 'lightgrey', 'edgecolor': 'white', 'hatch': '///', 'label': 'No contributions'}
        )
        #ax_map.set_title(f"{value_col} by Country", fontsize=14, weight='bold')
        ax_map.set_axis_off()
        ax_map.set_ylim([-55, 90])
        ax_map.set_xlim([-180, 180])


        # Add colorbar linked to the map scale
        sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=norm)
        sm.set_array([])
        ticks = [0, 10, 20, 30] 
        cbar = fig.colorbar(sm, ax=ax_map, fraction=0.025, pad=0.02, shrink=0.75, location="left", anchor=(-0.5, 0.5), ticks=ticks)
        cbar.ax.tick_params(labelsize=18)
        #cbar.set_label("Contributions to the NCQG (USDbn)")

        # Top-20 bar chart
        top20 = (
            df[["Country", value_col]].dropna().sort_values(by=value_col, ascending=False).head(20)
        )
        top20 = pd.merge(top20, df, how="left", on=["Country", value_col])

        # Plot bars with colors matching the map's colormap
        y_labels = top20['Country'].tolist()[::-1]  # largest at top
        y_values = top20[value_col].tolist()[::-1]
        bar_colors = [cmap_obj(norm(v)) for v in y_values]

        if value_col == "UMIC_No_US":
            rc = top20["Robust_Contribution"]
            no_us = top20["UMIC_No_US"]
            top20["Difference"] = no_us - rc
            avg = top20["Difference"].mean()
            avg_increase = np.nanmean(top20["Difference"]/top20["Robust_Contribution"])
            print(f"Average increase as a result of the USA is USD{avg}bn ({avg_increase*100}%) -" + value_col)
            # Base: With US and then increase
            top20_sorted = top20.sort_values(by=value_col, ascending=False)
            ax_bar.barh(top20_sorted["Country"], top20_sorted["Robust_Contribution"],  color=bar_colors)
            ax_bar.barh(top20_sorted["Country"], top20_sorted["Difference"], left=top20_sorted["Robust_Contribution"],  color=bar_colors, hatch='\\\\', edgecolor="black")
            ax_bar.invert_yaxis()
        elif value_col == "HIC_No_US":
            rc = top20["HIC"]
            no_us = top20["HIC_No_US"]
            top20["Difference"] = no_us - rc
            avg = top20["Difference"].mean()
            avg_increase = np.nanmean(top20["Difference"]/top20["HIC"])
            print(f"Average increase as a result of the USA is USD{avg}bn ({avg_increase*100}%) -" + value_col)
            # Base: With US and then increase
            top20_sorted = top20.sort_values(by=value_col, ascending=False)
            ax_bar.barh(top20_sorted["Country"], top20_sorted["HIC"],  color=bar_colors)
            ax_bar.barh(top20_sorted["Country"], top20_sorted["Difference"], left=top20_sorted["HIC"],  color=bar_colors, hatch='\\\\', edgecolor="black")
            ax_bar.invert_yaxis()
        else:
            ax_bar.barh(y_labels, y_values, color=bar_colors)

        ax_bar.set_xlabel("Contributions to the NCQG (USDbn p.a.)", fontsize=20)
        ax_bar.tick_params(axis='both', which='major', labelsize=18)
        ax_bar.set_title(label, fontsize=20, weight='bold')
        ax_bar.grid(axis='x', linestyle='--', alpha=0.3)

        # Optional: expand x-limits slightly for label readability
        try:
            x_max = max(y_values)
            ax_bar.set_xlim(0, x_max * 1.1 if x_max > 0 else x_max * 0.95)

            if value_col == ("HIC_No_US") or ("HIC"):
                ax_bar.set_xlim([0, 70])
        except ValueError:
            pass

        plt.savefig(savepath, bbox_inches='tight', dpi=dpi)
        plt.close(fig)



    def plot_map_and_top20_allocations(self,
                            df: pd.DataFrame,
                            value_col: str,
                            cmap: str,
                            savepath: str,
                            label: str,
                            dpi=300):
        """
        Helper that draws:
          - Top: global choropleth map of contributions in `value_col` with colorbar
          - Bottom: top-20 horizontal bar chart for `value_col`

        Args:
            df: DataFrame with columns ['ISO', 'Country', value_col]
            value_col: name of the contribution column to visualize
            cmap: matplotlib colormap
            savepath: file path to save the figure
            dpi: output resolution
        """
        # Load Natural Earth lowres polygons and join by ISO3
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)


        plot_df = world.merge(
            df[['ISO', 'Country', value_col]],
            left_on='ADM0_A3',
            right_on="ISO",
            how='left'
        )
        
        # Determine color scaling
        data_series = df[value_col].dropna()
        if data_series.empty:
            raise ValueError(f"No data available in column '{value_col}' to plot.")
        vmin = float(data_series.min())
        vmax = 5
        if vmin == vmax:
            # Avoid zero range; expand slightly
            vmin = vmin - 1e-9
            vmax = vmax + 1e-9

        cmap_obj = get_cmap(cmap)
        norm = Normalize(vmin=0, vmax=vmax)

        # Figure layout
        fig_map, ax_map = plt.subplots(figsize=(16, 10))
        fig_bar, ax_bar = plt.subplots(figsize=(16, 10))


        # Plot world choropleth
        plot_df.plot(
            column=value_col,
            ax=ax_map,
            cmap=cmap_obj,
            vmin=0,
            vmax=vmax,
            linewidth=0.2,
            edgecolor='white',
            missing_kwds={'color': 'lightgrey', 'edgecolor': 'white', 'hatch': '///', 'label': 'No contributions'}
        )
        #ax_map.set_title(f"{value_col} by Country", fontsize=14, weight='bold')
        ax_map.set_axis_off()
        ax_map.set_ylim([-55, 90])
        ax_map.set_xlim([-180, 180])

        # Add colorbar linked to the map scale
        sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=norm)
        sm.set_array([])
        ticks = [0, 1, 2, 3, 4, 5] 
        cbar = fig_map.colorbar(sm, ax=ax_map, fraction=0.025, pad=0.02, shrink=0.75, 
                                location="left", anchor=(-0.5, 0.5), ticks=ticks, extend="max")
        cbar.ax.tick_params(labelsize=18)
        cbar.set_label("Annual NCQG flows (USDbn p.a.)", fontsize=20)

        # Top-20 bar chart
        top20 = (
            df[['Country', value_col]].dropna().sort_values(by=value_col, ascending=False).head(30)
        )

        # Plot bars with colors matching the map's colormap
        y_labels = top20['Country'].tolist()[::-1]  # largest at top
        y_values = top20[value_col].tolist()[::-1]
        bar_colors = [cmap_obj(norm(v)) for v in y_values]

        
        ax_bar.barh(y_labels, y_values, color=bar_colors)
        ax_bar.set_xlabel("Annual flows to receipients under the NCQG (USDbn p.a.)", fontsize=20)
        ax_bar.tick_params(axis='both', which='major', labelsize=18)
        ax_bar.set_title(label, fontsize=20, weight='bold')
        ax_bar.grid(axis='x', linestyle='--', alpha=0.3)

        ax_map.text(0.02, 0.94, "a", transform=ax_map.transAxes, fontsize=20, fontweight='bold')
        ax_bar.text(0.02, 0.96, "b", transform=ax_bar.transAxes, fontsize=20, fontweight='bold')
        # Optional: expand x-limits slightly for label readability
        try:
            x_max = max(y_values)
            ax_bar.set_xlim(0, x_max * 1.1 if x_max > 0 else x_max * 0.95)
        except ValueError:
            pass

        fig_map.savefig(savepath, bbox_inches='tight', dpi=dpi)
        fig_bar.savefig(savepath + "_bar", bbox_inches='tight', dpi=dpi)
        plt.close(fig_map)
        plt.close(fig_bar)

    def make_sankey_flows_net(self, 
        source_col: str = "Country",          # country name in contributions (sources)
        contrib_col: str = "Contribution",    # contribution amount
        target_col: str = "Country",          # country name in distributions (targets)
        dist_col: str = "Distribution",       # distribution amount
        allow_negative_inputs: bool = False,  # allow negative inputs (both c and d)
        min_value: float = None,    # drop flows smaller than this
        round_to: float = None,       # round flow values to N decimals
        sort_desc: bool = True                # sort by value descending
    ) -> pd.DataFrame:
        """
        Build a Sankey-ready DataFrame with columns [source, target, value].

        Net distribution per target is computed as:
            n_j = max(d_j - c_j, 0)
        Shares are:
            Share_j = n_j / sum_j n_j
        Flows:
            v_ij = c_i * Share_j

        Parameters
        ----------
        contributions : DataFrame with [source_col, contrib_col]
        distributions : DataFrame with [target_col, dist_col]
        source_col    : Name of source country column in contributions
        contrib_col   : Contribution amount column
        target_col    : Name of target country column in distributions
        dist_col      : Distribution amount column
        allow_negative_inputs : If False, disallow negative contributions/distributions
        min_value     : Optional threshold to filter small flows
        round_to      : Optional decimals to round flow values
        sort_desc     : Sort flows by value descending

        Returns
        -------
        DataFrame with columns [source, target, value]
        """
        # Select relevant columns and drop NaNs
        c = self.contributions[[source_col, contrib_col]].dropna()
        d = self.allocations[[target_col, dist_col]].dropna()

        # Ensure there are no negatives in distributions (already clipped)
        # Drop zero-net targets to reduce noise (optional but harmless)
        d = d[d[dist_col] > 0].copy()

        # Check that there is positive net distribution to split
        net_total = d[dist_col].sum()
        if net_total <= 0:
            raise ValueError("Sum of net distributions is 0 after subtraction; cannot compute shares.")

        # Compute shares
        d["Share"] = d[dist_col] / net_total

        # Correct for if the quantum does not file
        d[dist_col] = d[dist_col] * net_total / d[dist_col].sum()
        c[contrib_col] = c[contrib_col] * net_total / c[contrib_col].sum()

        # Prepare vectors
        sources = c[source_col].to_numpy()
        targets = d[target_col].to_numpy()
        contrib_vals = c[contrib_col].to_numpy()
        share_vals = d["Share"].to_numpy()

        # Outer product to compute all flows
        flows_matrix = np.outer(contrib_vals, share_vals)  # shape: (n_sources, n_targets)

        # Long form DataFrame
        flows = (
            pd.DataFrame(flows_matrix, index=sources, columns=targets).stack().reset_index()
        )
        flows.columns = ["source", "target", "value"]

        # Optional filtering/rounding/sorting
        if min_value is not None:
            flows = flows[flows["value"] >= float(min_value)]

        if round_to is not None:
            flows["value"] = flows["value"].round(int(round_to))

        if sort_desc:
            flows = flows.sort_values("value", ascending=False).reset_index(drop=True)

        # Sanity check: sum of flows equals total contributions (shares sum to 1)
        total_contrib = c[contrib_col].sum()
        if not np.isclose(flows["value"].sum(), total_contrib):
            raise RuntimeError("Flow totals do not match total contributions. Check inputs.")
        
        # Merge on ISOs
        iso = self.contributions[[target_col, "ISO"]]
        flows = pd.merge(flows, iso, how="left", left_on="target", right_on=target_col)
        flows = pd.merge(flows, self.regions[["ISO", "Region"]], how="left", on="ISO")
        flows = flows.rename(columns={"ISO":"Target_ISO"})

        # Do the same for sources
        flows = pd.merge(flows, iso, how="left", left_on="source", right_on=source_col)
        flows = pd.merge(flows, self.regions[["ISO", "Region"]], how="left", on="ISO")
        flows = flows.rename(columns={"ISO":"Source_ISO"})


        return flows
    


    def build_sankey_grouped_by_region(self,
        flows: pd.DataFrame,
        *,
        source_col: str = "source",
        target_col: str = "target",
        value_col: str = "value",   # column in `regions` that has country names
        region_col: str = "Region",        # column in `regions` that has region names
        threshold_billion: float = 3,    # X in billions
        group_suffix: str = " (grouped)",  # suffix added to region labels for grouped nodes
        drop_self_loops: bool = True,      # drop flows where aggregated source == target
    ):
        """
        Collapse countries whose inflow/outflow does not exceed a threshold into their regions,
        aggregate flows, and produce Sankey-ready data.

        Inputs
        ------
        flows : DataFrame with [source_col, target_col, value_col]
        regions : DataFrame mapping countries to regions with [country_col, region_col]
        threshold_billion : Threshold X in billions. Nodes with max(inflow, outflow) <= X are grouped.
        return_indexed : If True, also return dict with 'nodes' (list) and 'links' (DataFrame with indices).

        """

        # Validate inputs
        for col in (source_col, target_col, value_col):
            if col not in flows.columns:
                raise ValueError(f"flows missing required column '{col}'.")

        df = flows[[source_col, target_col, value_col, "Target_ISO", "Source_ISO"]].copy()
        #df.dropna(subset=[source_col, target_col, value_col, "Target_ISO", "Source_ISO"], inplace=True)

        # Compute inflow/outflow per country FALLS TO 163 BN HERE
        inflow = df.groupby(target_col, as_index=True)[value_col].sum()
        outflow = df.groupby(source_col, as_index=True)[value_col].sum()

        # Union of all nodes appearing as source/target
        nodes = pd.Index(sorted(set(df[source_col]).union(set(df[target_col]))))

        # Align inflow/outflow to all nodes, fill missing with 0
        inflow = inflow.reindex(nodes, fill_value=0.0)
        outflow = outflow.reindex(nodes, fill_value=0.0)

        # Major/minor classification
        is_major = (np.maximum(inflow.values, outflow.values) > threshold_billion)
        node_status = pd.DataFrame({
            "node": nodes,
            "inflow": inflow.values,
            "outflow": outflow.values,
            "is_major": is_major
        })

        # Build country->region map
        regions = self.regions
        region_map = regions.set_index("ISO")[region_col].to_dict()

        # Map function: country -> aggregated label
        def map_node(country: str) -> str:
            if country in node_status[node_status["is_major"]]["node"].values:
                return country  # keep major node as-is
            region = region_map.get(country, None)
            return f"{region}{group_suffix}"

        # Apply mapping to sources and targets
        df["source_grouped"] = df["source"]
        df["target_grouped"] = df["Target_ISO"].map(map_node)

        # Optionally drop self-loops after grouping
        if drop_self_loops:
            df = df[df["source_grouped"] != df["target_grouped"]].copy()

        # Aggregate flows after grouping
        grouped_flows = (
            df.groupby(["source_grouped", "target_grouped"], as_index=False)[value_col].sum().rename(columns={"source_grouped": "source", "target_grouped": "target"})
        )


        return grouped_flows
    



    def plot_sankey_from_grouped(self,
        grouped_flows: pd.DataFrame,
        *,
        source_col: str = "source",
        target_col: str = "target",
        value_col: str = "value",
        palette: list[str] | None = None,  # optional region color palette
        node_colors_by_label: dict[str, str] | None = None,  # optional explicit node label -> color
        node_pad: int = 12,
        node_thickness: int = 18
    ):
        """
        Plot a Sankey diagram from pre-grouped flows.

        Parameters
        ----------
        grouped_flows : DataFrame with columns [source_col, target_col, value_col]
        regions       : Optional DataFrame with columns [country_col, region_col] to color nodes by region.
                        If node labels end with group_suffix (e.g., 'Europe (grouped)'), their region is inferred
                        directly from the label. Otherwise, region is looked up via `regions`.
        node_colors_by_label : Optional explicit mapping: node label -> color. Overrides region palette for those labels.

        Returns
        -------
        fig : plotly.graph_objects.Figure
        """

        # Basic validation
        for col in (source_col, target_col, value_col):
            if col not in grouped_flows.columns:
                raise ValueError(f"grouped_flows is missing required column '{col}'.")

        df = grouped_flows[[source_col, target_col, value_col]].copy()
        df = df.dropna(subset=[source_col, target_col, value_col])

        # Build node list and index map
        # Using sorted labels for stable ordering
        node_labels = sorted(set(df[source_col]).union(set(df[target_col])))
        node_index = {label: i for i, label in enumerate(node_labels)}

        



        # Build colors
        # Priority: explicit node color mapping > region palette > fallback palette
        if node_colors_by_label is None:
            node_colors_by_label = {}

        if palette is None:
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
                "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
                "#bcbd22", "#17becf"
            ]
        unique_regions = list(dict.fromkeys(node_labels))  # deterministic order
        node_colors  = {r: palette[i % len(palette)] for i, r in enumerate(unique_regions)}


        node_colors_list = [node_colors.get(lbl, "#999999") for lbl in node_labels]

        # Build links with indices
        links = df.copy()
        links["source_idx"] = links[source_col].map(node_index)
        links["target_idx"] = links[target_col].map(node_index)


        # Create figure
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                label=node_labels,
                color=node_colors_list,
                pad=node_pad,
                thickness=node_thickness
            ),
            link=dict(
                source=links["source_idx"],
                target=links["target_idx"],
                value=links[value_col],
            )
        )])

        # Saves a fully interactive file you can open in any browser
        fig.write_html("sankey.html", include_plotlyjs="cdn", full_html=True)

        return fig



data = Data()
#data.produce_contributions_figure()
flows = data.make_sankey_flows_net(source_col="Country",
                       contrib_col = "HIC",
                       target_col= "Country",
                       dist_col="Robust_Share",
                       allow_negative_inputs=False)
grouped_flows = data.build_sankey_grouped_by_region(
    flows=flows,
    threshold_billion=5,    
)
data.plot_sankey_from_grouped(grouped_flows=grouped_flows)
test = data
                                    