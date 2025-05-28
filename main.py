import random
from datetime import datetime

from github import get_github_stats
from svg import (
    generate_profile_lines,
    render_combined_svg,
)

ASCII_IMAGE = """
      *                     *@       
     }                        @@     
    }                          @@    
                  -      -   )  )@   
                             -   @   
  @                              @   
  }                      @-    - *@  
  ) @@@@@@@)      *@@@-@ @ @@@   @@@@
  @@        @}    })  @)     @   @*@)
      @ @@@ )}   }  ) @@ @@}     @  -
  @          )   ))              )@ -
                 *                  -
  @      -   }   *@               } -
  @}               }        }    @@ -
  @         - }*}}               @   
   @      * @@   @@@          @@ @ - 
   @     @@@@@@@@@@@@@@   @ @  ) @  @
    )  @@@ @         @@@@      }     
    @) @*@             @@  @    @ } )
     @ @@  )@@@@@@@@    @  @- @@@ @ *
      @) @@           )      @@@ @@@ 
       @@@ @     }   @@@*   -@      @
       @@@@ @     ) }  @@@-}@@       
          @@@@ @  @*@@@@   @@    )   
      @)  @  @  @}@ -  @ @    @   @@@
""".strip().splitlines()

COLOR_SCHEMES = [
    {
        "label": "#7FDBFF",  # Sky Blue
        "value": "#FFFFFF",  # White
        "ascii": "#AAAAAA",  # Light Gray
        "background": "#001F3F",  # Navy
        "ascii_image": "#FFFFFF"
    },
    {
        "label": "#FF6B6B",  # Coral
        "value": "#F7FFF7",  # Mint Cream
        "ascii": "#4ECDC4",  # Turquoise
        "background": "#2C3E50",  # Dark Blue
        "ascii_image": "#FFE66D"  # Yellow
    },
    {
        "label": "#9B59B6",  # Purple
        "value": "#ECF0F1",  # Light Gray
        "ascii": "#3498DB",  # Blue
        "background": "#2C3E50",  # Dark Blue
        "ascii_image": "#E74C3C"  # Red
    },
    {
        "label": "#2ECC71",  # Emerald
        "value": "#FDFEFE",  # White
        "ascii": "#F1C40F",  # Yellow
        "background": "#1A1A1A",  # Dark Gray
        "ascii_image": "#E74C3C"  # Red
    },
    {
        "label": "#E67E22",  # Orange
        "value": "#F5F6FA",  # Light Gray
        "ascii": "#95A5A6",  # Gray
        "background": "#2C3E50",  # Dark Blue
        "ascii_image": "#3498DB"  # Blue
    },
]

profile_template = {
    "alexei@quick":
        {
            "System":
                {
                    "OS": "Arch (btw) / Windows (ew)",
                    "Uptime": "",
                    "Host": "Winning Group",
                    "Kernel": "Senior Machine Learning Engineer",
                    "IDE": "neovim",
                },
            "Languages":
                {
                    "Programming": "Python, JavaScript, Lua, MATLAB",
                    "Real": "English, Japanese",
                },
            "Computer": {
                "Tools": "Docker, k8s, Linux",
                "Cloud": "AWS, GCP",
            },
            "Hobbies": {
                "Software": "AI/ML, DL",
                "Hardware": "AFL, Fitness, Cooking, Golf",
            },
        },
    "Contact":
        {
            "Email.Personal": "alexei.quick@gmail.com",
            "Email.Work": "alexei.quick@winning.com.au",
            "LinkedIn": "alexeiquick",
        },
    "Personal GitHub Stats": {
        "Repos": "",
        "Commits": "",
        "Lines of Code": "",
    }
}


def get_uptime_since(start_date: str = "1994-07-18") -> str:
    """
    Compute the duration since a given start date in YY:MM:DD format.

    Parameters
    ----------
    start_date : str
        The starting date in YYYY-MM-DD format.

    Returns
    -------
    str
        The duration since the start date in the format YY:MM:DD.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    today = datetime.today()

    years = today.year - start.year
    months = today.month - start.month
    days = today.day - start.day

    # Adjust for negative days and months
    if days < 0:
        months -= 1
        prev_month = (today.month - 1) or 12
        prev_year = today.year if today.month > 1 else today.year - 1
        last_month_day_count = (
            datetime(prev_year, prev_month + 1, 1) - datetime(prev_year, prev_month, 1)
        ).days
        days += last_month_day_count

    if months < 0:
        years -= 1
        months += 12

    return f"{years:02}:{months:02}:{days:02}"


def main():
    """
    Generate the SVG profile card with a random color scheme.
    """
    random_index = random.randint(0, len(COLOR_SCHEMES) - 1)
    colors = COLOR_SCHEMES[random_index]

    # Get GitHub stats
    github_stats = get_github_stats()["github"]

    # Update profile data with dynamic stats
    profile_template["alexei@quick"]["System"]["Uptime"] = get_uptime_since()
    profile_template["Personal GitHub Stats"] = {
        "Repos": f"{github_stats['repos']:,}",
        "Commits": f"{github_stats['commits']:,}",
        "Lines of Code": f"{github_stats['added']:,}",
    }

    # Generate lines
    profile_lines = generate_profile_lines(profile_template)
    svg_output = render_combined_svg(ASCII_IMAGE, profile_lines, colors)

    # Save
    with open("profile_card.svg", "w", encoding="utf-8") as f:
        f.write(svg_output)

    overwrite_readme_with_svg_remote()

    return


def overwrite_readme_with_svg_remote() -> None:
    """
    Overwrite the README.md file with an <img> tag pointing to the raw 
    GitHub-hosted SVG.
    """
    raw_url = "https://raw.githubusercontent.com/alexeiquickcode/alexeiquickcode/main/profile_card.svg"
    markdown = f'<img src="{raw_url}" alt="profile card"/>\n'

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)


if __name__ == '__main__':
    main()
